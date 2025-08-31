import math
from db_utils import SQLClass
from ui import UI
from settings import SettingsManager
from models import ProximityObject

class AppControler:
    def __init__(self):
        self.db = SQLClass()
        self.settings_manager = SettingsManager()
        self.ui = ui = UI(None, "Aurora Map Viewer", self, (600, 500))
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
        self.ui.id_select_panel.Hide()
        self.ui.main_menu_panel.Layout()
        self.ui.main_menu_panel.Show()
        self.ui.main_menu_panel.title.SetFocus()
    def make_list_default(self):
        self.pinned_object = self.Master_object_list[-1]
        self.view_list = self.Master_object_list
        self.apply_filters()
        self.sort_from_object()
    def toggle_setting(self, key, value):
        value = not value
        self.settings_manager.change_setting(key, value)
    def apply_filters(self):
        self.view_list =[i for i in self.Master_object_list if self.settings_manager.settings[i.object_type]]
        self.sort_from_object()
    def search_list(self, query):
        query = query.lower().split()
        results  = [("placeholder value", 1)]
        for i in self.Master_object_list:
            item_words = i.name.lower().split()
            score = 0
            for j in query:
                if j in item_words:
                    score += 1
            for item in range(len(results)):
                try:
                    if score >= results[item][1]:
                        results.insert(item, (i, score))
                except (IndexError, TypeError):
                    results.append((i, score))
        del results[-1]
        results =[i[0] for i in results]
        return results[:20]
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
                if object_amount >= int(amount) and object_access >= float(access):
                    score += object_amount
                    continue
                else:
                    break
            else:
                results.append((score, i))
        sorted_results =sorted(results, reverse=True)
        results=[i[1] for i in sorted_results]
        return results
    def handle_closing(self):
        if self.db.connection != None:
            self.db.close()
    def handle_change_game(self, event):
        """Handle change game button click"""
        pass
    
    def handle_change_race(self, event):
        """Handle change race button click"""
        pass
    
    def handle_change_system(self, event):
        """Handle change system button click"""
        pass
    
    def handle_view_list(self, event):
        """Handle view list button click"""
        pass
    
    def handle_edit_filter_settings(self, event):
        """Handle edit filter settings button click"""
        pass
    
    def handle_apply_filters(self, event):
        """Handle apply filters button click"""
        pass
    
    def handle_pin_item(self, event):
        """Handle pin item button click"""
        pass
    
    def handle_sort_from_pinned(self, event):
        """Handle sort from pinned button click"""
        pass
    
    def handle_calc_distance(self, event):
        """Handle calculate distance button click"""
        pass
    
    def handle_reset_sorting(self, event):
        """Handle reset sorting button click"""
        pass
    
    def handle_mineral_search(self, event):
        """Handle mineral search button click"""
        pass
            
