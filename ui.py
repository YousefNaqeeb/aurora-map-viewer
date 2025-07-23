import wx
class UI(wx.Frame):
    def __init__(self, parent, title, size):
        super().__init__(None, title=title, size=size)
        
        # Main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel = wx.Panel(self)
        self.main_sizer.Add(self.content_panel, 1, wx.ALL|wx.EXPAND, 10)
        self.button_panel = wx.Panel(self)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_panel.SetSizer(self.button_sizer)
        self.main_sizer.Add(self.button_panel, 0, wx.ALL, 5)
        self.button_panel.Hide()
        self.SetSizer(self.main_sizer)
        self.Center()
        self.Show()
        
    def show_message(self, message, is_error = False):
        """used to print what ever is sent to it."""
        if is_error:
            print(f"An error has occured, {message}")
        else:
            print(message)
    def prompt_for_input(self, prompt_text):
        """gets input from the user"""
        return input(f"{prompt_text}: ")
    def select_from_list(self, data):
        while True:
            try: #makes sure the choice is a correct value
                choice = data[int(self.prompt_for_input("Enter the number corresponding to the option you would like to select.")) - 1]
                return choice
            except (ValueError, TypeError, IndexError):
                self.show_message("You must enter a valid number.")
                continue
    def show_multiple_elements(self, data):
        for index, value in enumerate(data, start=1):
            self.show_message(f"{index}, {str(value)}")
        
    def show_options_and_get_input(self, data, message):
        """this function takes data and displays it to the user, then returns specific data that the user selected."""
        self.show_message(message)
        if len(data) == 1: #returns the first item if there is only one
            self.show_message("There was only one option, which has been selected for you automaticly.")
            return data[0]
        while True:
            self.show_multiple_elements(data)
            return self.select_from_list(data)
    def main_menu(self):
        """gets user input to return a command to main."""
        options = [
            "exit",
            "change game",
            "change race",
            "change system",
            "view list",
            "edit filter settings",
            "apply filters",
            "pin item",
            "sort list from pinned item",
            "calculate distance between pinned item and another item",
            "reset list sorting",
            "mineral search"]
        self.show_message("Main menu:")
        self.show_multiple_elements(options)
        return self.select_from_list(options)
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
    def edit_settings(self, settings):
        self.show_message("current settings:")
        for index, (key, value) in enumerate(settings.items(), start=1):
            print(f"{index}, {key}: {value}")
        while True:
            try:
                choice = int(self.prompt_for_input("Enter the number for the setting you would like to change, or 0 for done."))
                if choice == 0:
                    return "done"
                return list(settings)[choice - 1]
            except (ValueError, TypeError, IndexError):
                self.show_message("Invalid option.")
