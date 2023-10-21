def validate_game(game: str):
    from common.config import game_config
    if game not in game_config.games:
        raise ValueError(f"Invalid Game: {game}")
    
def validate_game_and_mode(game: str, mode: str):
    from common.config import game_config, competitive_config
    if game not in game_config.games:
        raise ValueError(f"Invalid Game: {game}")
    
    if game not in competitive_config.games or mode not in competitive_config.games[game].modes:
        raise ValueError(f"Invalid Game Mode: {mode}")
    
def validate_country_code(country: str):
    from common.config import countries_config
    if country not in countries_config.countries:
        raise ValueError(f"Invalid Country Code: {country}")