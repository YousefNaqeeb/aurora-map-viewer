import json
class SettingsManager:
    def __init__(self):
        self.settings = self.load_settings()
        self.save_settings()
    def load_settings(self):
        """loads settings for filtering data"""
        try:
            with open("settings.json", mode="r", encoding="utf-8") as read_file:
                return json.load(read_file)
        except (FileNotFoundError, json.JSONDecodeError): # If the file doesn't exist or is unreadable, save it with everything set to true
            default_settings = {
                "lifepod": True,
                "mass_driver_packet": True,
                "grav_survey_location": True,
                "jumppoint": True,
                "wreck": True,
                "body": True,
                "colony": True,
                "fleet": True,
                "missile_salvo": True,
                "weapon_contact": True,
                "star": True}
            return default_settings
    
    def save_settings(self):
        """Saves settings to settings.json"""
        with open("settings.json", mode="w", encoding="utf-8") as write_file:
            json.dump(self.settings, write_file, indent=4)
    def change_setting(self, key, value):
        """Change a specific setting"""
        self.settings[key] = value
        self.save_settings()
