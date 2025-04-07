from dataclasses import dataclass

from common.data.models.tournaments import TournamentDBFields, TournamentS3Fields

@dataclass
class TournamentTemplateRequestData(TournamentDBFields, TournamentS3Fields):
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
