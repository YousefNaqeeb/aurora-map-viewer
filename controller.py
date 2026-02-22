import math
import pyperclip
from db_utils import SQLClass
from ui import UI
from settings import SettingsManager
from models import ProximityObject

class AppControler:
    def __init__(self):
        self.db = SQLClass()
        self.settings_manager = SettingsManager()
        self.ui = UI(None, "Aurora Map Viewer", self, (600, 500))
        self.game_id = None
        self.race_id = None
        self.system_id = None
        self.system_name = None
        self.Master_object_list = []
        self.view_list = []
        self.pinned_object = None
        self.ui.update_status("Establishing connection to DB.")
        result = self.db.connect()
        if result[1]:
            self.ui.update_status(result[0])
        else:
            self.ui.update_status(result[0], True)
            self.ui.Close()
        self.get_starting_data()
    def get_starting_data(self):
        """Get game ID, then call the function that gets system and race data"""
        games = self.db.get_games()
        self.ui.select_from_list(games, "Select a game to load.", self.on_change_game)
    
    def on_change_game(self, game_id):
        """fully loads all game data and stores IDs"""
        self.game_id = game_id
        self.change_race()
        
    def change_race(self):
        """Get race data, then call function to get system data in on event"""
        player_races = self.db.get_player_races(self.game_id)
        self.ui.select_from_list(player_races, "Select which race you would like to load.", self.on_change_race)
    
    def on_change_race(self, race_id):
        """updates race and system information"""
        self.race_id = race_id
        self.change_system()
    
    def change_system(self):
        """Get system ID and data"""
        systems = self.db.get_systems(self.game_id, self.race_id)
        self.ui.select_from_list(systems, "Select a system to load.", self.on_change_system)

    def on_change_system(self, system_id):
        """updates system information hide panel, and show main menu"""
        self.system_id = system_id
        self.Master_object_list = self.db.get_system_data(self.game_id, self.race_id, self.system_name, self.system_id)
        self.make_list_default()
        self.show_main_menu()
    
    def show_main_menu(self):
        self.ui.clear_screen()
        self.ui.show_main_menu()
    
    def make_list_default(self):
        self.ui.view_objects_panel.text.SetLabel("")
        self.pinned_object = self.Master_object_list[-1]
        self.view_list = self.Master_object_list
        self.sort_from_object()
        self.apply_filters()
    
    def pin_item(self,  item):
        self.pinned_object = item.object
        self.sort_from_object()
        self.view_list_objects()
        self.ui.view_objects_panel.text.SetLabel(f"sorting list from {self.pinned_object.name}")
        self.ui.view_objects_panel.Layout()
    
    def copy_list(self, event):
            combobox = event.GetEventObject().combo
            data = '\n'.join(combobox.GetStrings())
            pyperclip.copy(data)
    def view_list_objects(self):
        self.ui.display_list_system_objects(self.view_list, self.pin_item)

    def get_settings(self):
        return self.settings_manager.settings
    
    def toggle_setting(self, key, value):
        self.settings_manager.change_setting(key, value)
    
    def show_wp_panel(self, item):
        self.ui.show_wp_panel   (item)
        
    def show_settings(self):
        self.ui.show_settings_panel()
    
    def apply_filters(self):
        self.view_list =[i for i in self.Master_object_list if self.settings_manager.settings[i.object_type]]
        self.sort_from_object()
        
    def find_distance(self, other):
        return round(math.dist(self.pinned_object, other))

    def find_bearing(self, item):
        """find angle with atan2, then convert it so 0 degrees is north instead of east"""
        delta_x = item.x - self.pinned_object.x
        delta_y = item.y - self.pinned_object.y
        angle_r = math.atan2(delta_y, delta_x)
        bearing = round(math.degrees(angle_r))
        bearing = (450 - bearing) % 360 # Rotate the number so 0 is north
        return bearing
    def sort_from_object(self):
        """Sorts the viewing list by distance, and gives each object an angle from the center point"""
        sorted_list = []
        for i in self.view_list:
            if type(i) == ProximityObject:
                item = i.object
            else:
                item = i
            distance = self.find_distance(item)
            bearing = self.find_bearing(item)
            sorted_list.append(ProximityObject(item, distance, bearing))
        self.view_list = sorted(sorted_list, key=lambda obj: obj.distance)
    def mineral_search(self, search_targets):
        """Find and return list of bodies with the requested minerals amounts and access levels"""
        results = []
        list_bodies =[i for i in self.Master_object_list if i.object_type == "body"] # Get rid of stuff that can't have minerals
        for i in list_bodies:
            score = 0
            for j in search_targets:
                mineral, amount, access = j
                object_amount, object_access = i.minerals[mineral]
                if object_amount >= amount and object_access >= access:
                    score += object_amount
                    continue
                else:
                    break
            else:
                results.append((score, i))
        sorted_results =sorted(results, reverse=True)
        results=[i[1] for i in sorted_results]
        self.ui.display_list_system_objects(results, self.pin_item)
    def handle_closing(self):
        if self.db.connection != None:
            self.db.close()
            self.ui.Close()
    
    def handle_mineral_search(self, event):
        """Handle mineral search button click"""
        self.ui.show_mineral_search_panel()

    def add_wp(self, x, y, wp_type, name, follow_id):
        wp_ids = self.db.get_wp_ids(self.game_id, self.race_id)
        ids = [i[0] for i in wp_ids]
        for i in range(1, 999): # The WaypointID can't be duplicated or larger than 999, but order doesn't matter, so checking starting from 1 should give a valid wp id
            if i in ids:
                continue
            else:
                wp_id = i
                break
        wp_num = max([i[1] for i in wp_ids], default=0) + 1
        creation_time = self.db.get_game_time(self.game_id)[0][0]
        if wp_type == 10:
            fleet_id = follow_id
            follow_id = 0
        else:
            fleet_id = 0
        columns = (wp_id, self.game_id, self.race_id, self.system_id, follow_id, creation_time, x, y, wp_num, wp_type, name, 0, fleet_id)
        self.db.add_wp(columns)
