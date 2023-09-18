from dataclasses import dataclass
from common.config.common import load_config

@dataclass
class CountriesData:
    countries: list[str]
    regions: dict[str, list[str]]

countries_data = load_config("countries.json", CountriesData)