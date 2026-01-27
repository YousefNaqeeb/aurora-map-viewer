import sqlite3
from math import ceil
from pathlib import Path
from models import BaseSystemObject, BaseBody, NPRPop, PlayerPop, Fleet, MissileSalvo
class ConnectionFaildError(Exception):
    """error for if the programme attempts to connect to AuroraDB.db wen it is not there"""
class SQLClass:
    """class to manage connections and queries also get data from db"""
    def __init__(self):
        """connects to auroraDB.db as soon as it is instantiated"""
        self.connection = None
        self.cursor = None
    def connect(self):
        """attempts to connect to the db and add indexes. if it can do so, it will return that the connection was established and true , oelse, it will return an error and false."""
        try:
            db_path = Path("auroraDB.db")
            if not db_path.exists():
                raise ConnectionFaildError("Could not find the file auroraDB.db. Make sure it is in the same directory.")
            self.connection = sqlite3.connect("auroraDB.db")
            self.cursor = self.connection.cursor()
            self.cursor.executescript("""
CREATE INDEX IF NOT EXISTS idx_mod_systembody_lookup ON FCT_SystemBody (GameID, SystemID, Name);
CREATE INDEX IF NOT EXISTS idx_mod_mineral_deposit_lookup ON FCT_MineralDeposit (SystemBodyID);
CREATE INDEX IF NOT EXISTS idx_mod_population_player_colonies ON FCT_Population (GameID, RaceID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_alienpop_lookup ON FCT_AlienPopulation (GameID, ViewingRaceID);
CREATE INDEX IF NOT EXISTS idx_mod_jumppoint_survey ON FCT_RaceJumpPointSurvey (RaceID, WarpPointID);
CREATE INDEX IF NOT EXISTS idx_mod_jumppoint_lookup ON FCT_JumpPoint (GameID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_fleet_lookup ON FCT_Fleet (GameID, SystemID, RaceID);
CREATE INDEX IF NOT EXISTS idx_mod_ship_fleet_lookup ON FCT_Ship (FleetID);
CREATE INDEX IF NOT EXISTS idx_mod_shipclass_pk_lookup ON FCT_ShipClass (ShipClassID);
CREATE INDEX IF NOT EXISTS idx_mod_wrecks_lookup ON FCT_Wrecks (GameID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_lifepods_lookup ON FCT_Lifepods (GameID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_missilesalvo_lookup ON FCT_MissileSalvo (GameID, SystemID);""")
            return ("Connection established.", True)
        except Exception as e:
            return (f"{e}", False)
# Helper function to     SQL queries with optional parameters
    def execute(self, query, variables = ()):
        self.cursor.execute(query, variables)
        return self.cursor.fetchall()
    def close(self):
        #close connection and drop indexes
        self.cursor.executescript("""
                                  DROP INDEX IF EXISTS idx_mod_systembody_lookup;
                                  DROP INDEX IF EXISTS idx_mod_mineral_deposit_lookup;
DROP INDEX IF EXISTS idx_mod_population_player_colonies;
DROP INDEX IF EXISTS idx_mod_alienpop_lookup;
DROP INDEX IF EXISTS idx_mod_jumppoint_survey;
DROP INDEX IF EXISTS idx_mod_jumppoint_lookup;
DROP INDEX IF EXISTS idx_mod_fleet_lookup;
DROP INDEX IF EXISTS idx_mod_ship_fleet_lookup;
DROP INDEX IF EXISTS idx_mod_shipclass_pk_lookup;
DROP INDEX IF EXISTS idx_mod_wrecks_lookup;
DROP INDEX IF EXISTS idx_mod_lifepods_lookup;
DROP INDEX IF EXISTS idx_mod_missilesalvo_lookup;""")
        self.connection.close()
        self.connection = None
        self.cursor = None

    def get_games(self):
        """This function returns a list of all games with IDs in the db"""
        return self.execute("SELECT GameID, GameName FROM FCT_Game")

    def get_player_races(self, game_id):
        """Gets a list of tuples containing all non npr races and there IDs"""
        return self.execute("SELECT RaceID, RaceTitle FROM FCT_Race WHERE NPR = 0 AND GameID = ?", (game_id,))
    # Function to load all system objects for the specified system
    def get_systems(self, game_id, race_id):
        """This function gets a list of all systems that a race has detected in the current game."""
        return self.execute("SELECT SystemID, Name FROM FCT_RaceSysSurvey  WHERE raceID = ? AND GameID = ?", (race_id, game_id))
    def get_system_data(self, game_id, race_id, system_name, system_id):
        """Loads all important data"""
        LIST_MINERALS =["duranium", "neutronium", "corbomite", "tritanium", "boronide", "mercassium", "vendarite", "sorium", "uridium", "corundium", "gallicite"] #list of minerals used to load mass driver packets and planets
        #Start loading lifepods in system
        self.cursor.execute("SELECT Xcor, Ycor, ShipName, Crew FROM FCT_Lifepods WHERE GameID = ? AND SystemID = ?", (game_id, system_id))
        list_system_objects = [BaseSystemObject(f"lifepod from {row[2]}", row[0], row[1], f"the lifepod has {row[3]} survivers on board", "lifepod") for row in self.cursor.fetchall()]
        # Load mass driver packets and their contents
        self.cursor.execute("""SELECT FCT_MassDriverPackets.*, FCT_Population.PopName FROM FCT_MassDriverPackets
        JOIN FCT_Population ON MassDriverDest = DestID 
        WHERE SysID = ? AND FCT_MassDriverPackets.GameID = ?""", (int(system_id), int(game_id)))
        for row in self.cursor.fetchall():
            # Extract mineral contents from the packet, and match the numbers to the correct mineral
            list_indexes =[i for i in range(13, 24) if row[i] > 0]
            packet_contents =[f"{LIST_MINERALS[i -13]}: {ceil(row[i])} tons" for i in list_indexes ]
            list_system_objects.append(BaseSystemObject(f"mass driver packet destination {row[-1]}", row[7], row[8], f"the packet contains {', '.join(packet_contents)}", "mass_driver_packet"))
            #load grav survey locations
        self.cursor.execute("SELECT * FROM  FCT_SurveyLocation WHERE GameID = ? AND SystemID = ?", (game_id, system_id))
        list_system_objects +=[BaseSystemObject(f"survey Point {row[3]}", row[4], row[-1], "", "grav_survey_location") for row in self.cursor.fetchall()]
        #load discovered jumppoints
        self.cursor.execute("""SELECT FCT_JumpPoint.WPLink, Xcor, Ycor, Explored FROM FCT_JumpPoint
    JOIN FCT_RaceJumpPointSurvey ON FCT_JumpPoint.WarpPointID = FCT_RaceJumpPointSurvey.WarpPointID
    WHERE FCT_RaceJumpPointSurvey.RaceID = ? AND FCT_JumpPoint.GameID = ? AND Charted = 1 AND SystemID = ?""", (race_id, game_id, system_id))
        for row in self.cursor.fetchall():
            if row[3] == 1:
                # For explored jump points, show destination system
                result = self.execute("""SELECT  FCT_JumpPoint.SystemID, FCT_RaceSysSurvey .Name FROM FCT_JumpPoint
                        JOIN FCT_RaceSysSurvey ON FCT_JumpPoint.SystemID = FCT_JumpPoint.SystemID
                        WHERE FCT_JumpPoint.WarpPointID = ?""", (row[0],))
                list_system_objects.append(BaseSystemObject(f"Jumppoint too the system {result[1]}", row[1], row[2], "", "jumppoint"))
            else:
                #for unexplored JPs
                list_system_objects.append(BaseSystemObject("Unexplored Jumppoint", row[1], row[2], "", "jumppoint"))
        #load wrecks
        self.cursor.execute("""SELECT FCT_Wrecks.ClassID, FCT_ShipClass.ClassName, xcor, ycor FROM FCT_Wrecks
        JOIN FCT_ShipClass ON FCT_Wrecks.ClassID = FCT_ShipClass.ShipClassID
        WHERE FCT_Wrecks.gameID = ? and FCT_Wrecks.SystemID = ?""", (game_id, system_id))
        list_system_objects +=[BaseSystemObject(f"Wreck of a {row[1]} class ship", row[2], row[3], "", "wreck") for row in self.cursor.fetchall()]
        #load only uncolonized bodies, to avoid having duplicated objects
        all_planets = {} # For properly naming moons
        for row in self.execute(
            """SELECT FCT_SystemBody.Name, xcor, ycor, PlanetNumber, OrbitNumber, BodyClass, FCT_SystemBody.SystemBodyID,
            COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 1 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat1_Amount,
            COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 1 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat1_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 2 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat2_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 2 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat2_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 3 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat3_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 3 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat3_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 4 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat4_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 4 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat4_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 5 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat5_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 5 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat5_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 6 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat6_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 6 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat6_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 7 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat7_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 7 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat7_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 8 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat8_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 8 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat8_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 9 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat9_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 9 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat9_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 10 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat10_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 10 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat10_Accessibility,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 11 THEN FCT_MineralDeposit.Amount ELSE 0 END), 0) AS Mat11_Amount,
    COALESCE(MAX(CASE WHEN FCT_MineralDeposit.MaterialID = 11 THEN FCT_MineralDeposit.Accessibility ELSE 0 END), 0) AS Mat11_Accessibility
                                FROM FCT_SystemBody
                                LEFT JOIN FCT_SystemBodySurveys ON FCT_SystemBodySurveys.SystemBodyID = FCT_SystemBody.SystemBodyID
                                LEFT JOIN FCT_MineralDeposit ON FCT_MineralDeposit.SystemBodyID = FCT_SystemBodySurveys.SystemBodyID
        WHERE FCT_SystemBody.GameID = ? AND FCT_SystemBody.systemID = ?
        GROUP BY FCT_SystemBody.SystemBodyID""", (game_id, system_id)):
            if row[5] == 1: # Planets
                if row[0] != "":
                    name = row[0]
                else:
                    name = f"{system_name} {row[3]}"
                object_type = "planet"
                all_planets[row[3]] = name
            elif row[5] == 2: # Moons
                if row[0] != "":
                    name = row[0]
                else:
                    name = f"{all_planets[row[3]]} moon {row[4]}"
                object_type = "moon"
            elif row[5] == 3: # Asteroids
                name = row[0]
                object_type = "asteroid"
            elif row[5] == 5:
                name = row[0]
                object_type = "comet"
            amounts = row[5::2]
            access = row[6::2]
            unformatted_minerals = zip(LIST_MINERALS, amounts, access)
            minerals ={mineral: (amount, access) for mineral, amount, access in unformatted_minerals}
            list_system_objects.append(BaseBody(name, row[1], row[2], "", object_type, minerals, row[6]))
        # Load colonized bodies not belonging to the player race
        self.cursor.execute("""SELECT EMSignature, ThermalSignature, PopulationName, xcor, ycor FROM FCT_AlienPopulation
                    JOIN FCT_systemBody ON FCT_Population.SystemBodyID = FCT_systemBody .SystemBodyID
                    JOIN FCT_Population ON FCT_AlienPopulation.PopulationID = FCT_Population.PopulationID
                    WHERE FCT_AlienPopulation.gameID = ? and ViewingRaceID = ? AND FCT_Population.SystemID = ?""", (game_id, race_id, system_id))
        list_system_objects +=[NPRPop(row[2], row[3], row[4], "", "colony", row[0], row[1]) for row in self.cursor.fetchall()]
        # Load colonized bodies belonging to the player
        for row in self.execute("""SELECT  PopulationID, Population, PopName, FCT_SystemBody.Xcor, FCT_SystemBody.Ycor FROM FCT_Population
        JOIN FCT_SystemBody ON FCT_Population.SystemBodyID = FCT_SystemBody.SystemBodyID
        WHERE FCT_Population.GameID = ? AND FCT_Population.RaceID = ? AND FCT_Population.SystemID = ?""", (game_id, race_id, system_id,)):
            try:
                # Get tracking station info (DSP = Deep Space Tracking station)
                dsp_amount =self.execute("SELECT Amount FROM FCT_PopulationInstallations WHERE GameID = ? AND PopID = ? AND PlanetaryInstallationID = 11", (game_id, row[0],))[0]
                dsp_strength = self.execute("SELECT PlanetarySensorStrength FROM FCT_Race WHERE RaceID = ? AND GameID = ?", (race_id, game_id))[0][0]
                dsp_strength *= dsp_amount # Calculate total tracking strength
            except Exception:
                dsp_strength = 0
            list_system_objects.append(PlayerPop(row[2], row[3], row[4], "", "colony", dsp_strength, row[1]))
            #load fleet data
        for row in self.execute("""SELECT FCT_Fleet.FleetID, FleetName, Speed, Xcor, Ycor,
                                GROUP_CONCAT(ShipName, ', ') as ShipNames
                                FROM FCT_Fleet
                                JOIN FCT_Ship ON FCT_Fleet.FleetID = FCT_Ship.FleetID
                                WHERE FCT_Fleet.GameID = ? AND FCT_Fleet.SystemID = ? AND FCT_Fleet.RaceID = ?
                                GROUP BY FCT_Fleet.FleetID""", (game_id, system_id, race_id)):
            if row[5] == None:
                list_system_objects.append(Fleet(row[1], row[3], row[4], "", "fleet", row[2], "empty fleet", row[0], True))
            else:
                list_system_objects.append(Fleet(row[1], row[3], row[4], "", "fleet", row[2], row[5], row[0], True))
        #load player missiles
        list_system_objects +=[MissileSalvo(f"Missile Salvo of {row[6]} missiles", row[3], row[4], "", "missile_salvo", row[5], row[7]) for row in self.execute("""SELECT MissileSalvoID, TargetType, TargetID, xcor, ycor, MissileSpeed, Name,
                                    COUNT(FCT_Missile.SalvoID) as MissileCount
            FROM FCT_MissileSalvo
            JOIN FCT_MissileType ON FCT_MissileSalvo.MissileID = FCT_MissileType.MissileID
            JOIN FCT_missile on FCT_MissileSalvo.MissileSalvoID = FCT_missile.SalvoID
            WHERE FCT_MissileSalvo.GameID = ? AND FCT_MissileSalvo.RaceID = ? AND FCT_MissileSalvo.SystemID = ?
            GROUP BY FCT_MissileSalvo.MissileSalvoID""", (game_id, race_id, system_id))]
        #load non player fleets
        list_system_objects +=[Fleet("", row[0], row[1], "", "fleet", row[2], row[-1], row[3], False) for row in self.execute("""SELECT FCT_Fleet.Xcor, FCT_Fleet.Ycor, FCT_Fleet.speed, FCT_Fleet.FleetID,
        GROUP_CONCAT(ShipID) as ShipIDs,
        GROUP_CONCAT(ContactName, ', ') as ShipNames
        FROM FCT_Fleet
        JOIN FCT_Ship ON FCT_Fleet.FleetID = FCT_Ship.FleetID
        JOIN FCT_Contacts on ContactID = ShipID
        WHERE ContactMethod <> 3 AND DetectRaceID = ? AND FCT_Fleet.GameID = ? AND FCT_Fleet.SystemID = ?
        GROUP BY FCT_Fleet.FleetID""", (race_id, game_id, system_id))]
        #load NPR missile salvos
        list_system_objects +=[MissileSalvo(f"NPR Missile Salvo of {row[6]} missiles", row[3], row[4], "", "missile_salvo", row[5], row[7]) for row in self.execute("""SELECT MissileSalvoID, TargetType, TargetID, FCT_MissileSalvo.xcor, FCT_MissileSalvo.ycor, MissileSpeed, Name,
                                    COUNT(FCT_Missile.SalvoID) as MissileCount
            FROM FCT_MissileSalvo
            JOIN FCT_MissileType ON FCT_MissileSalvo.MissileID = FCT_MissileType.MissileID
            JOIN FCT_missile on FCT_MissileSalvo.MissileSalvoID = FCT_missile.SalvoID
            JOIN FCT_Contacts ON FCT_MissileSalvo.MissileSalvoID = ContactID
            WHERE ContactType = 3 AND FCT_MissileSalvo.GameID = ? AND FCT_MissileSalvo.SystemID = ?
            GROUP BY FCT_MissileSalvo.MissileSalvoID""", (game_id, system_id))]
        #load weapon impact contacts, nuclear and energy weapons
        list_system_objects +=[BaseSystemObject(row[0], row[1], row[2], "", "weapon_contact") for row in self.execute("SELECT ContactName, xcor, ycor FROM FCT_Contacts WHERE ContactType IN (17, 18) AND GameID = ? AND DetectRaceID = ? AND SystemID = ?", (game_id, race_id, system_id))]
        # load LP's
        list_system_objects +=[BaseSystemObject(f"lp {num}, {all_planets[row[2]]}", row[0], row[1], '', "lp") for num, row in enumerate(self.execute(
            """SELECT FCT_LagrangePoint.Xcor, FCT_LagrangePoint.Ycor, FCT_SystemBody.PlanetNumber
            FROM FCT_LagrangePoint
            JOIN FCT_SystemBody ON FCT_LagrangePoint.PlanetID = FCT_SystemBody.SystemBodyID
            WHERE FCT_LagrangePoint.SystemID = ? AND FCT_LagrangePoint.GameID = ?""",
            (system_id, game_id)), start=1)]
        # Waypoints
        for row in self.execute("""SELECT Xcor, Ycor, Name, WaypointType, Number
                                  FROM FCT_Waypoint
                                  WHERE GameID = ? AND RaceID = ? AND SystemID = ?""", (game_id, race_id, system_id)):
            if row[3] == 0 and row[2] != "" or row[3] == 6 or row[3] == 10: # These all have names
                name = row[2]
            elif row[3] == 0:
                name = f"waypoint number {row[4]}"
            elif row[3] == 1:
                            name = f"point of interest number {row[4]}"
            elif row[3] == 2:
                name = f"Urgent POI number {row[4]}"
            elif row[3] == 8:
                name = f"temporary wp number {row[4]}"
            list_system_objects.append(BaseSystemObject(name, row[0], row[1], "", "wp"))
        list_system_objects.append(BaseSystemObject("central star", 0, 0, "", "star"))
        return list_system_objects
