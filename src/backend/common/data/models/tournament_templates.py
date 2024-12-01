from dataclasses import dataclass

from common.data.models.tournaments import CreateTournamentRequestData

@dataclass
class TournamentTemplateRequestData(CreateTournamentRequestData):
    template_name: str

@dataclass
class TournamentTemplate(TournamentTemplateRequestData):
    id: int | None

@dataclass
class TournamentTemplateMinimal():
    id: int
    template_name: str
    series_id: int | None

@dataclass
class TemplateFilter():
    series_id: int | None = None
