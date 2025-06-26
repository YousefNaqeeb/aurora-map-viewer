class AppControler:
    """Manages state of variables, will contain more app logic such as search. does not handle UI"""
    def __init__(self, db_handler, settings_manager):
        self.db = db_handler
        self.settings_manager = settings_manager
        self.game_id = None
        self.race_id = None
        self.system_id = None
        self.system_name = None
        self.system_objects = []
        self.view_list = []
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
        self.system_objects = self.db.get_system_data(self.game_id, self.race_id, self.system_name, self.system_id)
        self.view_list = self.system_objects
    def toggle_setting(self, key, value):
        value = not value
        self.settings_manager.change_setting(key, value)
    def apply_filters(self):
        self.view_list =[i for i in self.system_objects if self.settings_manager.settings[i.object_type]]