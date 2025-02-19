from dataclasses import dataclass
from common.data.commands import Command
from common.data.models import *

@dataclass
class CheckWordFilterCommand(Command[None]):
    request_body: dict[str, Any]

    async def handle(self, db_wrapper, s3_wrapper):
        # convert the request body into a string to check in the word filter
        string_body = ','.join(str(x).lower() for x in self.request_body.values())

        async with db_wrapper.connect() as db:
            async with db.execute("SELECT word FROM filtered_words WHERE ? LIKE '%'|| word ||'%'", (string_body,)) as cursor:
                bad_words = list(await cursor.fetchall())
                if len(bad_words):
                    raise Problem(f"The following bad words were found in your input: {', '.join(row[0] for row in bad_words)}")

@dataclass
class EditWordFilterCommand(Command[None]):
    words: FilteredWords

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM filtered_words")
            lowercase_words = set(w.lower().strip() for w in self.words.words)
            variable_parameters = [(w,) for w in lowercase_words]
            await db.executemany("INSERT INTO filtered_words(word) VALUES(?)", (variable_parameters))
            await db.commit()

@dataclass
class GetWordFilterCommand(Command[FilteredWords]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT word FROM filtered_words") as cursor:
                rows = await cursor.fetchall()
                words: list[str] = [row[0] for row in rows]
                return FilteredWords(words)