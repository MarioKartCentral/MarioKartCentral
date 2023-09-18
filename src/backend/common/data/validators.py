def validate_game(game: str):
    from common.config import game_data
    if game not in game_data.games:
        raise ValueError(f"Invalid Game: {game}")
    
def validate_game_and_mode(game: str, mode: str):
    from common.config import game_data, competitive_data
    if game not in game_data.games:
        raise ValueError(f"Invalid Game: {game}")
    
    if game not in competitive_data.games or mode not in competitive_data.games[game].modes:
        raise ValueError(f"Invalid Game Mode: {mode}")
    
def validate_country_code(country: str):
    from common.config import countries_data
    if country not in countries_data.countries:
        raise ValueError(f"Invalid Country Code: {country}")