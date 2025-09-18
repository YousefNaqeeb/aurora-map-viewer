import wx

def setup_frame_styling(frame):
    frame.SetBackgroundColour(wx.Colour(245, 245, 245))
    #frame.SetForegroundColour(wx.Colour(70, 130, 180))
    frame.sizer = wx.BoxSizer(wx.VERTICAL)
    frame.SetSizer(frame.sizer)


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
        self.main_sizer.Add(self.status_text, wx.ALL, 10)
        
        self.SetSizer(self.frame_sizer)
        self.id_select_panel = IDSelectPanel(self, self.controller)
        self.view_objects_panel = ViewListObjecctsPanel(self, controller)
        self.main_menu_panel = MainMenu(self, self.controller)
        self.settings_panel = FilterSettings(self, controller)

        
        self.panels = [self.id_select_panel, self.main_menu_panel, self.view_objects_panel, self.settings_panel]
        for i in self.panels:
            self.frame_sizer.Add(i, 1, wx.ALL|wx.EXPAND, 10)
        self.Center()
        self.Show()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        
    
    def on_close(self, event):
        self.update_status("closing program")
        self.controller.handle_closing()
        event.Skip()
    
    def clear_screen(self):
        for i in self.panels:
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
        self.id_select_panel.combo_box.Append([i[1] for i in data])
        self.id_select_panel.combo_box.object_map = {i: index[0] for i, index in enumerate(data)}
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
        self.main_menu_panel.SetFocus()

    def display_list_system_objects(self, view_list, callback):
        self.clear_screen()
        self.view_objects_panel.combo_box.Clear()
        self.view_objects_panel.callback = callback
        strs_items =[str(i) for i in view_list]
        self.view_objects_panel.combo_box.Append(strs_items)
        self.view_objects_panel.combo_box.object_map = {i: index for i, index in enumerate(view_list)}
        self.view_objects_panel.combo_box.SetFocus
        self.view_objects_panel.Show()
        self.view_objects_panel.Layout()
        self.view_objects_panel.SetFocus()
    
    def show_settings_panel(self):
        self.clear_screen()
        self.settings_panel.Layout()
        self.settings_panel.Show()
        self.settings_panel.SetFocus()

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
        
        self.Center()
        self.Layout()
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_select_from_combo)    
        
    def on_select_from_combo(self, event):
        index = self.combo_box.GetSelection()
        if index != wx.NOT_FOUND:
            item = self.combo_box.object_map[index]
            self.combo_box.Clear()
            self.callback(item)

class ViewListObjecctsPanel(IDSelectPanel):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        self.submit_btn.SetLabel("pin item")
        self.back_btn = wx.Button(self, label="back")
        self.Sizer.Add(self.back_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.show_main_menu())
        self.Layout()
    
class FilterSettings(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        setup_frame_styling(self)
        self.settings = self.controller.get_settings()
        self.checkboxes = []
        for setting, value in self.settings.items():
            new_checkbox = wx.CheckBox(self, label=setting)
            new_checkbox.SetValue(value)
            new_checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_clicked)
            self.sizer.Add(new_checkbox, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
            self.checkboxes.append(new_checkbox)
        
        self.back_btn =wx.Button(self, label="back")
        self.sizer.Add(self.back_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        self.Layout
        
    def on_checkbox_clicked(self, event):
        checkbox = event.GetEventObject()
        key = checkbox.GetLabel()
        value = checkbox.GetValue()
        self.controller.toggle_setting(key, value)
    
    def on_back(self, event):
        self.controller.show_main_menu()
        self.controller.apply_filters()
        
            
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
        self.reset_sorting_btn = wx.Button(self, label="Reset List Sorting")
        self.mineral_search_btn = wx.Button(self, label="Mineral Search")
        
        buttons = [
            self.exit_btn,
            self.change_game_btn,
            self.change_race_btn,
            self.change_system_btn,
            self.view_list_btn,
            self.edit_filter_btn,
            self.reset_sorting_btn,
            self.mineral_search_btn
        ]
        
        button_sizer = wx.GridSizer(cols=2, hgap=10, vgap=10)
        
        for button in buttons:
            button_sizer.Add(button, 0, wx.EXPAND)
        
        self.sizer.Add(button_sizer, 1, wx.ALL|wx.EXPAND, 20)
        
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.change_game_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.get_starting_data())
        self.change_race_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.change_race())
        self.change_system_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.change_system())
        self.view_list_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.view_or_pin_list())
        self.edit_filter_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.show_settings())
        self.reset_sorting_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.make_list_default())
        self.mineral_search_btn.Bind(wx.EVT_BUTTON, self.controller.handle_mineral_search)
        self.title.SetFocus()
    def on_exit(self, event):
        close_event = wx.CloseEvent(wx.wxEVT_CLOSE_WINDOW)
        self.GetParent().on_close(event)
