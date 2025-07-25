import wx
class UI(wx.Frame):
    def __init__(self, parent, title, controller, size):
        super().__init__(None, title=title, size=size)
        self.controller = controller
        # Main sizer
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        # Content panel
        self.main_panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)
        self.frame_sizer.Add(self.main_panel, 1, wx.ALL|wx.EXPAND, 10)
        # Button sizer
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.button_sizer, 0, wx.EXPAND)
        self.SetSizer(self.frame_sizer)
        self.Center()
        self.Show()
        # Event defenitions
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
    
    def on_close(self, event):
        self.show_message("closing program")
        self.controller.handle_closing()
        event.Skip()
    
    def clear_screen(self):
        self.content_sizer.Clear(delete_windows=True)
        self.button_sizer.Clear(delete_windows=True)
        self.main_panel.Layout
    
    def show_message(self, message, is_error = False):
        """used to display what ever is sent to it."""
        self.clear_screen() # Makes sure screen is ready for new messages an such
        if is_error:
            message = f"An error has occured, {message}"
        message_text = wx.StaticText(self.main_panel, label=message)
        self.content_sizer.Add(message_text, wx.ALL, 10)
        self.main_panel.Layout()
        self.Update()
        wx.CallAfter(message_text.SetFocus) # Makes sure focus is set so screenreaders read the message
    
    def prompt_for_input(self, prompt_text): # Fiishin convertig tis ater
        """gets input from the user"""
        """
        self.show_message(prompt_text)
        self.text_input = wx.TextCtrl(self.content_panel)
        self.content_panel.GetSizer().Add(self.text_input, wx.ALL|wx.EXPAND, 5)
        submit_button = wx.Button(self.button_panel, label="submit")
        self.button_panel.GetSizer().Add(submit_button, wx.ALL|wx.EXPAND, 5)
        """        
        return input(f"{prompt_text}: ")
    def select_from_list(self, data, message, callback):
        self.show_message(message)
        """makes a combo box for selecting items from a list with a callback"""
        combo_box = wx.ComboBox(self.main_panel, style=wx.CB_READONLY)
        for i in data:
            index = combo_box.Append(i[1])
            combo_box.SetClientData(index, i[0])
        self.content_sizer.Add(combo_box, wx.ALL|wx.EXPAND, 5)
        wx.CallAfter(combo_box.SetFocus)
        combo_box.callback = callback
        submit_btn  = wx.Button(self.main_panel, label="submit")
        submit_btn.SetCanFocus(True)
        self.button_sizer.Add(submit_btn, wx.ALL|wx.EXPAND, 5)
        self.main_panel.Layout()
        submit_btn.Bind(wx.EVT_BUTTON, self.on_select_from_combo)
        submit_btn.combo_box = combo_box
    def on_select_from_combo(self, event):
        combo_box = event.GetEventObject().combo_box
        index = combo_box.GetSelection()
        if index != wx.NOT_FOUND:
            item = combo_box.GetClientData(index)
            combo_box.callback(item)
    
    def show_multiple_elements(self, data):
        for index, value in enumerate(data, start=1):
            self.show_message(f"{index}, {str(value)}")
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
