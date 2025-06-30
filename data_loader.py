def get_system_data(db, ui, game_id, race_id):
    """Get system name and ID"""
    systems = db.get_systems(game_id, race_id)
    system_names = [system[1] for system in systems] # gives names to be displayed to the user
    chosen_system_name = ui.show_options_and_get_input(system_names, "Select a system to load.")
    match_dict = {name: (id, name) for id, name in systems}
    chosen_system_data = match_dict[chosen_system_name] # returns the ID that matches with the name
    return chosen_system_data

def get_race_data(db, ui, game_id):
    """Get race data, then call function to get system data"""
    player_races = db.get_player_races(game_id)
    race_names = [race[1] for race in player_races]
    chosen_race_name = ui.show_options_and_get_input(race_names, "Select which race you would like to load.")
    match_dict = {name: id for id, name in player_races}
    chosen_race = match_dict[chosen_race_name]
    chosen_system = get_system_data(db, ui, game_id, chosen_race)
    return (chosen_race, chosen_system)

def get_starting_data(db, ui):
    """Get game ID, then call the function that gets system and race data"""
    games = db.get_games()
    game_names = [i[1] for i in games]
    chosen_game_name = ui.show_options_and_get_input(game_names, "Select a game to load.")
    match_dict = {name: id for id, name in games}
    chosen_game = match_dict[chosen_game_name]
    chosen_race, chosen_system = get_race_data(db, ui, chosen_game)
    return (chosen_game, chosen_race, chosen_system)
