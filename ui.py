class UI:
    def show_message(self, message, is_error = False):
        """used to print what ever is sent to it."""
        if is_error:
            print(f"An error has occured, {message}")
        else:
            print(message)
    def prompt_for_input(self, prompt_text):
        """gets input from the user"""
        return input(f"{prompt_text}: ")
    def show_options_and_get_input(self, data, message):
        """this function takes a list of tuples and displays them to the user, then returns what ever valid tuple the user selects"""
        self.show_message(message)
        if len(data) == 1: #returns the first tuple if there is only one
            self.show_message("There was only one option, which has been selected for you automaticly.")
            return data[0]
        while True:
            choice = self.prompt_for_input("Type the name of what you would like to select, or leave blank to view all objects and choose from the list.")
            if choice == "": #wen the user leaves a blank line, and is taken to the list of options
                for index, value in enumerate(data, start=1):
                    self.show_message(f"{index}, {value[1]}")
                while True:
                    try: #makes sure the choice is a correct value
                        choice = data[int(self.prompt_for_input("Enter the number corresponding to the option you would like to select.")) - 1]
                        return choice
                    except (ValueError, TypeError, IndexError):
                        self.show_message("You must enter a valid number.")
                        continue
            else: #if the user types soething else
                for i in data:
                    if choice == i[1]:
                        return i
                    self.show_message("Could not find that option")
    def main_menu(self):
        """gets user input to return a command to main."""
        options = [
            "exit",
            "change game",
            "change race",
            "change system",
            "view list"]
        self.show_message("Main menu:")
        for index, value in enumerate(options, start = 1):
            self.show_message(f"{index}, {value}")
        while True:
            try: #user validation for main menu return
                choice = options[int(self.prompt_for_input("Enter the number corresponding to the option you would like to select")) - 1]
                return choice
            except (ValueError, TypeError, IndexError):
                self.show_message("You must enter a valid number.")
    def display_list_system_objects(self, view_list):
        """this fuction manages displaying the list of system object, currently, it is paged, with 20 items on each page."""
        page = 0
        page_start = page * 20
        page_end = page_start + 20
        index = page_start
        while index <= page_end + 1 and index <= len(view_list):
            page_start, page_end = page * 20, page_start + 20
            self.show_message(f"{index + 1}, {view_list[index]}")
            index += 1
            if index == page_end or index ==len(view_list):
                while True:
                    try:
                        choice = int(self.prompt_for_input("1, go back, 2, continue, 3, return to main menu"))
                        if choice == 1 and page == 0: #to make sure the user doesn't end up on a negative page
                            self.show_message("You can't go back at this time.")
                        elif choice == 1: #go back one page
                            page -= 1
                            index -= 20
                            break
                        elif choice == 2 and index == len(view_list): #to stop the index from being greater than the amount of elements in the list.
                            self.show_message("You can't continue at this time.")
                        elif choice == 2: #next page
                            page += 1
                            break
                        elif choice == 3:
                            return
                        else:
                            self.show_message("invalid option")
                    except ValueError:
                        self.show_message("You must enter valid data.")
