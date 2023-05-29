from typing import List
from dataclasses import asdict, dataclass
import msgspec
from common.data.commands import Command
from common.data.models import Problem, TemplateFilter, TournamentTemplate, TournamentTemplateMinimal, TournamentTemplateRequestData


@dataclass
class CreateTournamentTemplateCommand(Command[None]):
    body: TournamentTemplateRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body

        # we only need to put the template name and series ID into the database for querying, the rest can go into s3 since we won't be querying this
        async with db_wrapper.connect() as db:
            cursor = await db.execute("INSERT INTO tournament_templates (name, series_id) VALUES (?, ?)",
            (b.template_name, b.series_id))
            template_id = cursor.lastrowid
            await db.commit()

        s3_message = bytes(msgspec.json.encode(self.body))
        await s3_wrapper.put_object('templates', f'{template_id}.json', s3_message)

@dataclass
class EditTournamentTemplateCommand(Command[None]):
    body: TournamentTemplateRequestData
    template_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        b = self.body

        async with db_wrapper.connect() as db:
            cursor = await db.execute("""UPDATE tournament_templates
                SET name = ?,
                series_id = ?
                WHERE id = ?""", (b.template_name, b.series_id, self.template_id))
            updated_rows = cursor.rowcount
            if updated_rows == 0:
                raise Problem('No template found', status=404)
            

            s3_data = await s3_wrapper.get_object('templates', f'{self.template_id}.json')
            if s3_data is None:
                raise Problem("No template found", status=404)
            
            json_body = msgspec.json.decode(s3_data)
            updated_values = asdict(self.body)
            json_body.update(updated_values)

            s3_message = bytes(msgspec.json.encode(json_body))
            await s3_wrapper.put_object('templates', f'{self.template_id}.json', s3_message)
            await db.commit()

@dataclass
class GetTournamentTemplateDataCommand(Command[TournamentTemplate]):
    template_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        body = await s3_wrapper.get_object('templates', f'{self.template_id}.json')
        if body is None:
            raise Problem('No template found', status=404)
        template_data = msgspec.json.decode(body, type=TournamentTemplate)
        template_data.id = self.template_id
        return template_data

@dataclass
class GetTournamentTemplateListCommand(Command[List[TournamentTemplateMinimal]]):
    filter: TemplateFilter

    async def handle(self, db_wrapper, s3_wrapper):
        filter = self.filter
        async with db_wrapper.connect(readonly=True) as db:
            where_clauses = []
            variable_parameters = []

            def append_equal_filter(filter_value, column_name):
                if filter_value is not None:
                    where_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(filter_value)

            append_equal_filter(filter.series_id, "series_id")

            where_clause = "" if not where_clauses else f" WHERE {' AND '.join(where_clauses)}"

            template_query = f"SELECT id, name, series_id FROM tournament_templates{where_clause}"

            templates = []
            async with db.execute(template_query, variable_parameters) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    template_id, template_name, series_id = row
                    templates.append(TournamentTemplateMinimal(template_id, template_name, series_id))
            return templates