import math
from models import ProximityObject
class AppControler:
    """Manages state of variables, will contain more app logic such as search. does not handle UI"""
    def __init__(self, db_handler, settings_manager):
        self.db = db_handler
        self.settings_manager = settings_manager
        self.game_id = None
        self.race_id = None
        self.system_id = None
        self.system_name = None
        self.Master_object_list = []
        self.view_list = []
        self.pinned_object = None
    def load_starting_data(self, game_id, race_id, system_id, system_name):
        """fully loads all game data and stores IDs"""
        self.game_id = game_id
        self.change_race(race_id, system_id, system_name)
    def change_race(self, race_id, system_id, system_name):
        """updates race and system information"""
        self.race_id = race_id
        self.change_system(system_id, system_name)
    def change_system(self, system_id, system_name):
        """updates system information"""
        self.system_id = system_id
        self.system_name = system_name
        self.Master_object_list = self.db.get_system_data(self.game_id, self.race_id, self.system_name, self.system_id)
        self.make_list_default()
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
