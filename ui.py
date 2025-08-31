import wx


def setup_frame_styling(frame):
    frame.SetBackgroundColour(wx.Colour(245, 245, 245))
    frame.SetForegroundColour(wx.Colour(70, 130, 180))
    frame.sizer = wx.BoxSizer(wx.VERTICAL)


class UI(wx.Frame):
    def __init__(self, parent, title, controller, size):
        super().__init__(None, title=title, size=size)
        self.controller = controller
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        setup_frame_styling(self)
        self.main_panel.SetSizer(self.main_sizer)
        self.frame_sizer.Add(self.main_panel, 1, wx.ALL|wx.EXPAND, 10)
        
        self.status_text = wx.StaticText(self.main_panel, label="establishing connection")
        self.main_panel.SetForegroundColour(wx.Colour(70, 130, 180))
        self.sizer.Add(self.status_text, wx.ALL, 10)
        
        self.SetSizer(self.frame_sizer)
        self.id_select_panel = IDSelectPanel(self, self.controller)
        self.main_menu_panel = MainMenu(self, self.controller)
        self.panels = {"id_panel": self.id_select_panel, "main menu": self.main_menu_panel}
        for i in self.panels.values():
            self.frame_sizer.Add(i, 1, wx.ALL|wx.EXPAND, 10)
        self.Center()
        self.Show()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        
    
    def on_close(self, event):
        self.update_status("closing program")
        self.controller.handle_closing()
        event.Skip()
    
    def clear_screen(self):
        for i in self.panels.values():
            i.Hide()
    
    def update_status(self, message, is_error = False):
        """used to display what ever is sent to it."""
        if is_error:
            message = f"An error has occured, {message}"
        self.status_text.SetLabel(message)
        self.main_panel.Layout()
        self.Update()
        wx.CallAfter(self.status_text.SetFocus) # Makes sure focus is set so screenreaders read the message
    
    def prompt_for_input(self, prompt_text): # Fiishin convertig tis ater
        """gets input from the user"""
        """
        self.update_status(prompt_text)
        self.text_input = wx.TextCtrl(self.content_panel)
        self.content_panel.GetSizer().Add(self.text_input, wx.ALL|wx.EXPAND, 5)
        submit_button = wx.Button(self.button_panel, label="submit")
        self.button_panel.GetSizer().Add(submit_button, wx.ALL|wx.EXPAND, 5)
        """        
        return input(f"{prompt_text}: ")
    def select_from_list(self, data, message, callback):
        """passes data to the id select panel"""
        self.id_select_panel.SetFocus()
        self.id_select_panel.text.SetLabel(message)
        self.id_select_panel.callback = callback
        for i in data:
            index = self.id_select_panel.combo_box.Append(i[1])
            self.id_select_panel.combo_box.SetClientData(index, i[0])
        wx.CallAfter(self.id_select_panel.combo_box.SetFocus)
        self.id_select_panel.Show()
        self.id_select_panel.Layout()
        self.id_select_panel.SetFocus()
    
    def show_multiple_elements(self, data):
        for index, value in enumerate(data, start=1):
            self.update_status(f"{index}, {str(value)}")
    
    def show_main_menu(self):
        self.main_menu_panel.Layout()
        self.main_menu_panel.Show()
        self.main_menu_panel.title.SetFocus()

    def display_list_system_objects(self, view_list):
        """this fuction manages displaying the list of system object, currently, it is paged, with 20 items on each page."""
        page = 0
        page_start = page * 20
        page_end = page_start + 20
        index = page_start
        while index <= page_end + 1 and index <= len(view_list):
            page_start, page_end = page * 20, page_start + 20
            self.update_status(f"{index + 1}, {view_list[index]}")
            index += 1
            if index == page_end or index ==len(view_list):
                while True:
                    try:
                        choice = int(self.prompt_for_input("1, go back, 2, continue, 3, return to main menu"))
                        if choice == 1 and page == 0: #to make sure the user doesn't end up on a negative page
                            self.update_status("You can't go back at this time.")
                        elif choice == 1: #go back one page
                            page -= 1
                            index -= 20
                            break
                        elif choice == 2 and index == len(view_list): #to stop the index from being greater than the amount of elements in the list.
                            self.update_status("You can't continue at this time.")
                        elif choice == 2: #next page
                            page += 1
                            break
                        elif choice == 3:
                            return
                        else:
                            self.update_status("invalid option")
                    except ValueError:
                        self.update_status("You must enter valid data.")
    def edit_settings(self, settings):
        self.update_status("current settings:")
        for index, (key, value) in enumerate(settings.items(), start=1):
            print(f"{index}, {key}: {value}")
        while True:
            try:
                choice = int(self.prompt_for_input("Enter the number for the setting you would like to change, or 0 for done."))
                if choice == 0:
                    return "done"
                return list(settings)[choice - 1]
            except (ValueError, TypeError, IndexError):
                self.update_status("Invalid option.")

class IDSelectPanel(wx.Panel):
    """
    class with combo box and button for submitting. for giving user options with tuples where one option is the ID
    will return ID to controller from the on event
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        setup_frame_styling(self)
        self.message, self.data, self.callback = (None, None, None)
        self.text = wx.StaticText(self, label="")
        self.sizer.Add(self.text, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.combo_box = wx.ComboBox(self, style=wx.CB_READONLY)
        self.sizer.Add(self.combo_box, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 20)
        wx.CallAfter(self.combo_box.SetFocus)
        self.combo_box.callback = self.callback
        self.submit_btn  = wx.Button(self, label="submit")
        self.sizer.Add(self.submit_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.SetSizer(self.sizer)
        
        self.Center()
        self.Layout()
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_select_from_combo)
        
    def on_select_from_combo(self, event):
        index = self.combo_box.GetSelection()
        if index != wx.NOT_FOUND:
            item = self.combo_box.GetClientData(index)
            self.combo_box.Clear()
            self.callback(item)
class MainMenu(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        setup_frame_styling(self)
        self.title = wx.StaticText(self, label="Main Menu")
        title_font = self.title.GetFont()
        title_font.PointSize += 4
        title_font = title_font.Bold()
        self.title.SetFont(title_font)
        self.sizer.Add(self.title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        
        self.exit_btn = wx.Button(self, label="Exit")
        self.change_game_btn = wx.Button(self, label="Change Game")
        self.change_race_btn = wx.Button(self, label="Change Race")
        self.change_system_btn = wx.Button(self, label="Change System")
        self.view_list_btn = wx.Button(self, label="View List")
        self.edit_filter_btn = wx.Button(self, label="Edit Filter Settings")
        self.apply_filters_btn = wx.Button(self, label="Apply Filters")
        self.pin_item_btn = wx.Button(self, label="Pin Item")
        self.sort_from_pinned_btn = wx.Button(self, label="Sort List from Pinned Item")
        self.calc_distance_btn = wx.Button(self, label="Calculate Distance Between Pinned Item and Another Item")
        self.reset_sorting_btn = wx.Button(self, label="Reset List Sorting")
        self.mineral_search_btn = wx.Button(self, label="Mineral Search")
        
        buttons = [
            self.exit_btn,
            self.change_game_btn,
            self.change_race_btn,
            self.change_system_btn,
            self.view_list_btn,
            self.edit_filter_btn,
            self.apply_filters_btn,
            self.pin_item_btn,
            self.sort_from_pinned_btn,
            self.calc_distance_btn,
            self.reset_sorting_btn,
            self.mineral_search_btn
        ]
        
        button_sizer = wx.GridSizer(cols=2, hgap=10, vgap=10)
        
        for button in buttons:
            button_sizer.Add(button, 0, wx.EXPAND)
        
        self.sizer.Add(button_sizer, 1, wx.ALL|wx.EXPAND, 20)
        self.SetSizer(self.sizer)
        
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.change_game_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.get_starting_data())
        self.change_race_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.change_race())
        self.change_system_btn.Bind(wx.EVT_BUTTON, lambda evt: self/controller.change_system())
        self.view_list_btn.Bind(wx.EVT_BUTTON, self.controller.handle_view_list)
        self.edit_filter_btn.Bind(wx.EVT_BUTTON, self.controller.handle_edit_filter_settings)
        self.apply_filters_btn.Bind(wx.EVT_BUTTON, self.controller.handle_apply_filters)
        self.pin_item_btn.Bind(wx.EVT_BUTTON, self.controller.handle_pin_item)
        self.sort_from_pinned_btn.Bind(wx.EVT_BUTTON, self.controller.handle_sort_from_pinned)
        self.calc_distance_btn.Bind(wx.EVT_BUTTON, self.controller.handle_calc_distance)
        self.reset_sorting_btn.Bind(wx.EVT_BUTTON, self.controller.handle_reset_sorting)
        self.mineral_search_btn.Bind(wx.EVT_BUTTON, self.controller.handle_mineral_search)
        self.title.SetFocus()
    def on_exit(self, event):
        close_event = wx.CloseEvent(wx.wxEVT_CLOSE_WINDOW)
        self.GetParent().on_close(event)
