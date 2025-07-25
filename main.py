import wx
from controller import AppControler

def main():
    """Main function"""
    # Initialise all components
    app = wx.App()
    controller = AppControler()
    app.MainLoop()
    """
    while True: # Main loop
        choice = ui.main_menu()
        if choice == "exit":
            ui.show_message("Exiting program")
            db.close()
            break
        elif choice == "change game":
            chosen_game, chosen_race, chosen_system = get_starting_data(db, ui)
            ui.show_message(f"loading system {chosen_system[1]}")
            controller.load_starting_data(chosen_game, chosen_race, chosen_system[0], chosen_system[1])
            ui.show_message("Data loaded.")
        elif choice == "change race":
            chosen_race, chosen_system = get_race_data(db, ui, controller.game_id)
            controller.change_race(chosen_race, chosen_system[0], chosen_system[1])
            ui.show_message("Data updated")
        elif choice == "change system":
            chosen_system = get_system_data(db, ui, controller.game_id, controller.race_id)
            controller.change_system(chosen_system[0], chosen_system[1])
            ui.show_message("Data updated.")
        elif choice == "view list":
            ui.display_list_system_objects(controller.view_list)
        elif choice == "edit filter settings":
            while True:
                settings_choice =ui.edit_settings(settings_manager.settings)
                if settings_choice == "done":
                    break
                controller.toggle_setting(settings_choice, settings_manager.settings[settings_choice])
        elif choice == "apply filters":
            controller.apply_filters()
            ui.show_message("list updated")
        elif choice == "pin item":
            results = controller.search_list(ui.prompt_for_input("enter something to search"))
            if results == []:
                ui.show_message("Could not find what you were looking for.")
            else:
                pinned_object = ui.show_options_and_get_input(results, "Search found following results:")
                controller.pinned_object = pinned_object
        elif choice  == "sort list from pinned item":
            controller.sort_from_object()
        elif choice == "calculate distance between pinned item and another item":
            results = controller.search_list(ui.prompt_for_input("enter something to search"))
            if results == []:
                ui.show_message("Could not find what you were looking for.")
            else:
                item = ui.show_options_and_get_input(results, "Search found following results:")
                ui.show_message(f"distance {controller.find_distance(item)}, bearing: {controller.find_bearing(item)} degrees")
        elif choice == "reset list sorting":
            controller.make_list_default()
        elif choice == "mineral search":
            full_query= []
            while True:
                try:
                    query = ui.prompt_for_input("Enter the mineral you would like to search for, amount, and access seperated by a space. example, gallicite 250000 0.5, or enter done to search")
                    if query.lower() == "done" and len(full_query) == 0:
                        break
                    elif query == "done":
                        results =controller.mineral_search(full_query)
                        ui.show_multiple_elements(results)
                        break
                    query =query.split()
                    query[0].lower()
                    int(query[1])
                    float(query[2])
                    full_query.append(query)
                except (ValueError, KeyError):
                    ui.show_message("Invalid input")
        else:
            ui.show_message("Invalid option.")
            """
if __name__ == "__main__":
    main()
