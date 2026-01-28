import wx
import wx.lib.agw.floatspin

def setup_frame_styling(frame):
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
        self.base_select_panel = BaseSelectPanel(self, self.controller)
        self.view_objects_panel = ViewListObjectsPanel(self, self.controller)
        self.main_menu_panel = MainMenu(self, self.controller)
        self.settings_panel = FilterSettings(self, self.controller)
        self.mineral_search_panel = MineralSearchPanel(self, self.controller)
        self.create_wp_panel = WPCreationPanel(self, self.controller)
        
        self.panels = [self.base_select_panel, self.main_menu_panel, self.view_objects_panel, self.settings_panel, self.mineral_search_panel]
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
    
    def select_from_list(self, data, message, callback):
        """passes data to the id select panel"""
        self.base_select_panel.SetFocus()
        self.base_select_panel.text.SetLabel(message)
        self.base_select_panel.callback = callback
        self.base_select_panel.combo_box.Append([i[1] for i in data])
        self.base_select_panel.combo_box.object_map = {i: index[0] for i, index in enumerate(data)}
        wx.CallAfter(self.base_select_panel.combo_box.SetFocus)
        self.base_select_panel.Show()
        self.base_select_panel.Layout()
        self.base_select_panel.SetFocus()
    
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
    
    def show_wp_panel(self):
        self.clear_screen()
        self.create_wp_panel.Show()
        self.create_wp_panel.SetFocus()
        
    def show_settings_panel(self):
        self.clear_screen()
        self.settings_panel.Layout()
        self.settings_panel.Show()
        self.settings_panel.SetFocus()
    
    def show_mineral_search_panel(self):
        self.clear_screen()
        self.mineral_search_panel.Show()
        self.mineral_search_panel.SetFocus()

class BaseSelectPanel(wx.Panel):
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

class ViewListObjectsPanel(BaseSelectPanel):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        self.submit_btn.SetLabel("pin item")
        self.add_wp_btn = wx.Button(self, label="add WP")
        self.Sizer.Add(self.add_wp_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.copy_btn = wx.Button(self, label="copy list")
        self.copy_btn.combo = self.combo_box
        self.Sizer.Add(self.copy_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.back_btn = wx.Button(self, label="back")
        self.Sizer.Add(self.back_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.add_wp_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.show_wp_panel())
        self.copy_btn.Bind(wx.EVT_BUTTON, self.controller.copy_list)
        self.back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.show_main_menu())
        self.Layout()
    
class WPCreationPanel(BaseSelectPanel):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        
        self.combo_box.Append([
            "normal wp",
            "named WP",
            "Rendezvous WP",
            "Point of Interest",
            "Urgent POI",
            "Temporary WP",
            "fleet WP"
        ])
        
        self.combo_box.SetLabel("Select WP type")
        self.visibility_config = {
            0: (["name_field"], ["x_spin", "y_spin", "checkbox"]),
            1: ([], ["name_field", "x_spin", "y_spin", "checkbox"]),
            2: ([], ["name_field", "x_spin", "y_spin", "checkbox"]),
            3: (["name_field"], ["x_spin","y_spin", "checkbox"]),
            4: (["name_field"], ["x_spin", "y_spin", "checkbox"]),
            5: (["name_field"], ["x_spin", "y_spin", "checkbox"]),
            6: (["name_field", "x_spin", "y_spin", "checkbox"], []),
        }
        name_field = wx.TextCtrl(self)
        name_field.SetLabel("Enter A name for the Waypoint")
        self.Sizer.Add(name_field, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        x_spin = wx.SpinCtrlDouble(self, max=1000000000000)
        x_spin.SetLabel('x')
        self.Sizer.Add(x_spin, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        y_spin = wx.SpinCtrlDouble(self, max=1000000000000)
        y_spin.SetLabel('y')
        self.Sizer.Add(y_spin, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        attach_to_body_checkbox = wx.CheckBox(self, label="Attach to body")
        self.Sizer.Add(attach_to_body_checkbox, wx.ALL|wx.ALIGN_CENTRE_HORIZONTAL, 15)
        self.submit_btn.MoveAfterInTabOrder(attach_to_body_checkbox)
        self.back_btn = wx.Button(self, label="back")
        self.Sizer.Add(self.back_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        
        self.wp_widgets = {
            "name_field": name_field,
            "x_spin": x_spin,
            "y_spin": y_spin,
            "checkbox": attach_to_body_checkbox
        }
        self.Layout()
        
        self.change_ui((["name_field", "x_spin", "y_spin", "checkbox"], []))
        self.combo_box.Bind(wx.EVT_COMBOBOX, self.on_select_from_combo)
        self.back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.view_list_objects())
    
    def change_ui(self, items):
        """Set what things should be shown or hidden"""
        for i in items[0]:
            self.wp_widgets[i].Hide()
        for i in items[1]:
            self.wp_widgets[i].Show()
    
    def on_select_from_combo(self, event):
        selected_item = self.combo_box.GetSelection()
        ui_state = self.visibility_config[selected_item]
        self.change_ui(ui_state)

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
        
    
class MineralSearchPanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        setup_frame_styling(self)
        self.text = wx.StaticText(self, label="Mineral search")
        self.sizer.Add(self.text, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        
        self.spin_ctrls = []
        LIST_MINERALS =["duranium", "neutronium", "corbomite", "tritanium", "boronide", "mercassium", "vendarite", "sorium", "uridium", "corundium", "gallicite"]
        for i in LIST_MINERALS:
            lable = wx.StaticText(self, label=i)
            amount_spin = wx.SpinCtrl(self, max=2000000000)
            amount_spin.SetLabel(f"{i} amount")
            access_spin = wx.lib.agw.floatspin.FloatSpin(self, min_val=0.0, max_val=1.0, increment=0.1, digits=2)
            access_spin.SetLabel(f"{i} access level")
            amount_spin.access_spin = access_spin
            self.Sizer.Add(amount_spin, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
            self.Sizer.Add(access_spin, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
            self.spin_ctrls.append(amount_spin)
        
        self.search_btn = wx.Button(self, label="search")
        self.Sizer.Add(self.search_btn, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        self.Center()
        self.Layout()
    
    def on_search(self, event):
        search = []
        for i in self.spin_ctrls:
            if i.GetValue() >= 1:
                amount = i.GetValue()
                mineral = i.GetLabel().split()[0]
                access = i.access_spin.GetValue()
                search.append((mineral, amount, access))
            else:
                continue
        self.controller.mineral_search(search)
    
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
        self.view_list_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.view_list_objects())
        self.edit_filter_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.show_settings())
        self.reset_sorting_btn.Bind(wx.EVT_BUTTON, lambda evt: self.controller.make_list_default())
        self.mineral_search_btn.Bind(wx.EVT_BUTTON, self.controller.handle_mineral_search)
        self.title.SetFocus()
    def on_exit(self, event):
        close_event = wx.CloseEvent(wx.wxEVT_CLOSE_WINDOW)
        self.GetParent().on_close(event)
