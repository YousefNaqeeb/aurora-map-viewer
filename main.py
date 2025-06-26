import sys
from db_utils import SQLClass
from controler import AppControler
from ui import UI
from data_loader import get_starting_data, get_race_data, get_system_data
from settings import SettingsManager

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
    settings_manager = SettingsManager()
    controler = AppControler(db, settings_manager)
    chosen_game, chosen_race, chosen_system = get_starting_data(db, ui)
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
            chosen_game, chosen_race, chosen_system = get_starting_data(db, ui)
            ui.show_message(f"loading system {chosen_system[1]}")
            controler.load_starting_data(chosen_game, chosen_race, chosen_system[0], chosen_system[1])
            ui.show_message("Loaded data.")
        elif choice == "change race":
            chosen_race, chosen_system = get_race_data(db, ui, controler.game_id)
            controler.change_race(chosen_race, chosen_system[0], chosen_system[1])
            ui.show_message("data updated")
        elif choice == "change system":
            chosen_system = get_system_data(db, ui, controler.game_id, controler.race_id)
            controler.change_system(chosen_system[0], chosen_system[1])
            ui.show_message("Data updated.")
        elif choice == "view list":
            ui.display_list_system_objects(controler.view_list)
        elif choice == "edit filter settings":
            while True:
                settings_choice =ui.edit_settings(settings_manager.settings)
                if settings_choice == "done":
                    break
                controler.toggle_setting(settings_choice, settings_manager.settings[settings_choice])
        elif choice == "apply filters":
            controler.apply_filters()
            ui.show_message("list updated")
        else:
            ui.show_message("Invalid option.")
if __name__ == "__main__":
    main()
