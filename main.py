#from math import dist
from db_utils import SQLClass
# Main program
sql = SQLClass()
game_id = sql.get_game_id()
race_info = sql.get_race(game_id)
list_system_objects =sql.get_system_data(input("enter the system you would like to select, or leave blank to see a list of systems."), race_info, game_id)

# Main menu loop
while True:
    try:
        User_input =int(input("Select an option 0, exit 1, change to a different game, 2, view from another race, 3, view a different system 4, print all loaded objects"))
    except Exception as e:
        print("Invalid data")
        continue
    if User_input == 0:
        break
    elif User_input == 1:
        game_id =sql.get_game_id()
        race_info =sql.get_race(game_id)
        list_system_objects =sql.get_system_data(input("enter the system you would like to select, or leave blank to see a list of systems."), race_info, game_id)
    elif User_input == 2:
        race_info =sql.get_race(game_id)
        list_system_objects =sql.get_system_data(input("enter the system you would like to select, or leave blank to see a list of systems."), race_info, game_id)
    elif User_input == 3:
        list_system_objects =sql.get_system_data(input("enter the system you would like to select, or leave blank to see a list of systems."), race_info, game_id)
    elif User_input == 4:
        # Display all objects in current system with pagination (15 items per page)
        print("here is a list of all objects in the selected system")
        for index, value in enumerate(list_system_objects, start=1):
            print(f"{index}, {value}")
            EXIT_LOOP = False
            if index % 15 == 0 and index > 0:
                while True:
                    try:
                        User_input =int(input("1, continue, 2, stop viewing list."))
                        if User_input ==1:
                            break
                        elif User_input == 2:
                            EXIT_LOOP = True
                            break
                        else:
                            print("Invalid option.")
                    except Exception as e:
                        print("Invalid data")
            if EXIT_LOOP:
                break
sql.close()
