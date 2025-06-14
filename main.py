import sys
from db_utils import SQLClass
from controler import AppControler
from ui import UI
def _get_starting_data(db, ui):
    games = db.get_games()
    chosen_game = ui.show_options_and_get_input(games, "Select a game to load.")[0]
    player_races = db.get_player_races(chosen_game)
    chosen_race = ui.show_options_and_get_input(player_races, "Select which race you would like to load.")[0]
    systems = db.get_systems(chosen_game, chosen_race)
    chosen_system = ui.show_options_and_get_input(systems, "Select a system to load.")
    return (chosen_game, chosen_race, chosen_system)

def main():
    """main function"""
    #initialise all components
    ui = UI()
    db = SQLClass()
    ui.show_message("Establishing connection to DB.")
    result = db.connect()
    if result[1]:
        ui.show_message(result[0])
    else:
        ui.show_message(result[0], True)
        sys.exit()
    controler = AppControler(db)
    chosen_game, chosen_race, chosen_system = _get_starting_data(db, ui)
    ui.show_message(f"loading system {chosen_system[1]}")
    controler.load_starting_data(chosen_game, chosen_race, chosen_system[0], chosen_system[1])
    ui.show_message("Loaded data.")
    while True: #main loop
        choice = ui.main_menu()
        if choice == "exit":
            ui.show_message("exiting programme")
            db.close()
            break
        elif choice == "change game":
            chosen_game, chosen_race, chosen_system = _get_starting_data(db, ui)
            ui.show_message(f"loading system {chosen_system[1]}")
            controler.load_starting_data(chosen_game, chosen_race, chosen_system[0], chosen_system[1])
            ui.show_message("Loaded data.")
        elif choice == "change race":
            player_races = db.get_player_races(controler.game_id)
            chosen_race = ui.show_options_and_get_input(player_races, "Select which race you would like to load.")[0]
            systems = db.get_systems(controler.game_id, chosen_race)
            chosen_system = ui.show_options_and_get_input(systems, "Select a system to load.")
            controler.change_system(chosen_system[0], chosen_system[1])
            ui.show_message("data updated")
        elif choice == "change system":
            systems = db.get_systems(controler.game_id, chosen_race)
            chosen_system = ui.show_options_and_get_input(systems, "Select a system to load.")
            controler.change_system(chosen_system[0], chosen_system[1])
            ui.show_message("Data updated.")
        elif choice == "view list":
            print(type(controler.view_list))
            print(len(controler.view_list))
            ui.display_list_system_objects(controler.view_list)
        else:
            ui.show_message("Invalid option.")
if __name__ == "__main__":
    main()