import sqlite3
from math import ceil
import time
from models import BaseSystemObject, BaseDetectableObject, PlayerPop, PlayerFleet, PlayerMissileSalvo
class SQLClass:
    # class to manage connections and queries also get data from db.
    def __init__(self):
        #connects to auroraDB.db as soon as it is instantiated
        self.connection = None
        self.cursor = None
        self.connect()
    def connect(self):
        try:
            print("Establishing connection.")
            self.connection = sqlite3.connect("auroraDB.db")
            self.cursor = self.connection.cursor()
            self.cursor.executescript("""
CREATE INDEX IF NOT EXISTS idx_mod_systembody_lookup ON FCT_SystemBody (GameID, SystemID, Name);
CREATE INDEX IF NOT EXISTS idx_mod_population_lookup ON FCT_Population (RaceID, SystemID, GameID, PopName);
CREATE INDEX IF NOT EXISTS idx_mod_population_player_colonies ON FCT_Population (GameID, RaceID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_alienpop_lookup ON FCT_AlienPopulation (GameID, ViewingRaceID);
CREATE INDEX IF NOT EXISTS idx_mod_jumppoint_survey ON FCT_RaceJumpPointSurvey (RaceID, WarpPointID);
CREATE INDEX IF NOT EXISTS idx_mod_jumppoint_lookup ON FCT_JumpPoint (GameID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_fleet_lookup ON FCT_Fleet (GameID, SystemID, RaceID);
CREATE INDEX IF NOT EXISTS idx_mod_ship_fleet_lookup ON FCT_Ship (FleetID);
CREATE INDEX IF NOT EXISTS idx_mod_shipclass_pk_lookup ON FCT_ShipClass (ShipClassID);
CREATE INDEX IF NOT EXISTS idx_mod_wrecks_lookup ON FCT_Wrecks (GameID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_lifepods_lookup ON FCT_Lifepods (GameID, SystemID);
CREATE INDEX IF NOT EXISTS idx_mod_missilesalvo_lookup ON FCT_MissileSalvo (GameID, RaceID, SystemID);""")
            print("Connection established.")
        except Exception as e:
            print(f"Database connection error: {str(e)}")
# Helper function to     SQL queries with optional parameters
    def execute(self, query, variables = ()):
        self.cursor.execute(query, variables)
        return self.cursor.fetchall()
    def close(self):
        #close connection and drop indexes
        self.cursor.executescript("""
                                  DROP INDEX IF EXISTS idx_mod_systembody_lookup;
DROP INDEX IF EXISTS idx_mod_population_lookup;
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
        print("Connection closed.")
    # Function to get game ID by name or from a list
    def get_game_id(self):
        while True:
            game_name =input("Enter game name to load, or leave blank to see list of games.")
            if not game_name:
                #Display list of available games
                games =self.execute("SELECT GameName FROM FCT_Game")
                for index, value in enumerate(games, start=1):
                    print(f"{index}. {value}")
                try:
                    # Get selected game ID by index
                    game_id =self.execute("SELECT GameID from FCT_Game WHERE GameName = ?", (games[int(input("enter the number of the game you would like to select.")) - 1][0],))
                    return int(game_id[0][0])
                except Exception:
                    print("Invalid option.")
            else:
                # Get game ID directly by name
                game_id = self.execute("SELECT GameID from FCT_Game WHERE GameName = ?", (game_name,))
                if not game_id:
                    print("game not found. try again.")
                else:
                    return int(game_id[0][0])

    # Function to get player race ID
    def get_race(self, game_id):
        # Get player races (non-NPR) for the game
        race_info =  self.execute("SELECT RaceID, RaceTitle FROM FCT_Race WHERE NPR = 0 AND GameID = ?", (game_id,))
        if len(race_info) == 1:
            # If only one race, select it automatically
            return race_info[0][0]
        # Display list of races if multiple are available
        print("you can pick from the following options.")
        for index, value in enumerate(race_info, start=1):
            print(f"{index}, {value[1]}")
        # Get user selection
        while True:
            try:
                return race_info[int(input("enter the number of the race you would like to view.")) -1][0]
            except Exception:
                print("invalid option")

    # Function to load all system objects for the specified system
    # This is the main data retrieval function that populates the list of objects in a star system
    def get_system_data(self, system_name, race_id, game_id):
        while True:
            if not system_name == "":
                try:
                    # Attempt to get system ID by name if a specific system was requested
                    # FCT_RaceSysSurvey table contains systems that have been discovered by each race
                    system_id = self.execute("SELECT SystemID FROM FCT_RaceSysSurvey  WHERE name = ? AND raceID = ?", (system_name, race_id))[0][0]
                    break
                except Exception:
                    system_name =input("System not found. try again, or leave blank to view possible systems.")
            else:
                # If no system name provided, display list of all systems discovered by this race
                list_system_ids = self.execute("SELECT name, SystemID FROM FCT_RaceSysSurvey  WHERE raceID = ? AND GameID = ?", (race_id, game_id))
                print("You can select one of the following systems.")
                for index, value in enumerate(list_system_ids, start=1):
                    print(f"{index}, {value[0]}")
                # Get user selection from the displayed list
                while True:
                    try:
                        num =int(input("Enter the number for the system you would like to select.")) -1
                        system_name = list_system_ids[num][0]
                        system_id = list_system_ids[num][1]
                        break
                    except (ValueError, IndexError):
                        print("invalid option")
        # System found, begin loading all objects
        print(f"Loading system {system_name}")
        start_time = time.time()
        #Start loadin lifepods in system
        self.cursor.execute("SELECT Xcor, Ycor, ShipName, Crew FROM FCT_Lifepods WHERE GameID = ? AND SystemID = ?", (game_id, system_id))
        list_system_objects = [BaseSystemObject(f"lifepod from {row[2]}", row[0], row[1], f"the lifepod has {row[3]} survivers on board") for row in self.cursor.fetchall()]
        # Load mass driver packets and their contents
        self.cursor.execute("""SELECT FCT_MassDriverPackets.*, FCT_Population.PopName FROM FCT_MassDriverPackets
        JOIN FCT_Population ON MassDriverDest = DestID 
        WHERE SysID = ? AND FCT_MassDriverPackets.GameID = ?""", (int(system_id), int(game_id)))
        for row in self.cursor.fetchall():
            # Extract mineral contents from the packet, and match the numbers to the correct mineral
            list_indexes =[i for i in range(13, 24) if row[i] > 0]
            list_minerals =["Duranium", "Neutronium", "Corbomite", "Tritanium", "Boronide", "Mercassium", "Vendarite", "Sorium", "Uridium", "Corundium", "Gallicite"]
            packet_contents =[f"{list_minerals[i -13]}: {ceil(row[i])} tons" for i in list_indexes ]
            list_system_objects +=BaseSystemObject(f"mass driver packet destination {row[-1]}", row[7], row[8], f"the packet contains {', '.join(packet_contents)}")
            #load grav servay locations
        self.cursor.execute("SELECT * FROM  FCT_SurveyLocation WHERE GameID = ? AND SystemID = ?", (game_id, system_id))
        list_system_objects +=[BaseSystemObject(f"Servay Point {row[3]}", row[4], row[-1], "") for row in self.cursor.fetchall()]
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
                list_system_objects.append(BaseSystemObject(f"Jumppoint too the system {result[1]}", row[1], row[2], ""))
            else:
                #for unexplored JPs
                list_system_objects.append(BaseSystemObject("Unexplored Jumppoint", row[1], row[2], ""))
        #load wrecks
        self.cursor.execute("""SELECT FCT_Wrecks.ClassID, FCT_ShipClass.ClassName, xcor, ycor FROM FCT_Wrecks
        JOIN FCT_ShipClass ON FCT_Wrecks.ClassID = FCT_ShipClass.ShipClassID
        WHERE FCT_Wrecks.gameID = ? and FCT_Wrecks.SystemID = ?""", (game_id, system_id))
        list_system_objects +=[BaseSystemObject(f"Wreck of a {row[1]} class ship", row[2], row[3], "") for row in self.cursor.fetchall()]
        #load only uncolonized bodies, to avoid having duplicated objects
        for row in self.execute("""SELECT FCT_SystemBody.Name, xcor, ycor, PlanetNumber, OrbitNumber FROM FCT_SystemBody
        WHERE FCT_SystemBody.Name NOT IN
        (SELECT FCT_Population.PopName FROM FCT_Population WHERE FCT_Population.RaceID = ? AND FCT_Population.SystemID = ? AND FCT_Population.GameID = ?)
        AND FCT_SystemBody.GameID = ? AND FCT_SystemBody.systemID = ?""", (race_id, system_id, game_id, game_id, system_id)):
            if row[0] != "":
                list_system_objects.append(BaseSystemObject(row[0], row[1], row[2], ""))
            elif row[4] == 0:
                # makes sure all system bodies have a name. this branch makes sure planets are named correctly
                list_system_objects.append(BaseSystemObject(f"{system_name} {row[3]}", row[1], row[2], ""))
            else:
                #this handles moons
                list_system_objects.append(BaseSystemObject(f"{system_name} {row[3]} moon {row[4]}", row[1], row[2], ""))
        # Load colonized bodies not belonging to the player race
        self.cursor.execute("""SELECT EMSignature, ThermalSignature, PopulationName, xcor, ycor FROM FCT_AlienPopulation
                    JOIN FCT_systemBody ON FCT_Population.SystemBodyID = FCT_systemBody .SystemBodyID
                    JOIN FCT_Population ON FCT_AlienPopulation.PopulationID = FCT_Population.PopulationID
                    WHERE FCT_AlienPopulation.gameID = ? and ViewingRaceID = ? AND FCT_Population.SystemID = ?""", (game_id, race_id, system_id))
        list_system_objects +=[BaseDetectableObject(row[2], row[3], row[4], "", row[0], row[1]) for row in self.cursor.fetchall()]
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
            list_system_objects.append(PlayerPop(row[2], row[3], row[4], "", dsp_strength, row[1]))
            #load fleet data
        for row in self.execute("""SELECT FleetID, FleetName, Speed, Xcor, Ycor FROM FCT_Fleet WHERE GameID = ? AND SystemID = ? AND RaceID = ?""", (game_id, system_id, race_id)):
            #access FCT_Fleet, EMSensorStrength for EM, PassiveSensorStrength for th
            try: #to handle fleets with ships
                ships, sensor_data, last_class_id = [], [], 0
                for i in self.execute("SELECT ShipClassID, ShipName FROM FCT_Ship WHERE FleetID = ?", (row[0],)):
                    ships.append(i[1])
                    new_class_id= i[0]
                    if last_class_id != new_class_id:
                        #makes sure no data is duplicated
                        last_class_id = new_class_id
                        sensor_data.append(self.execute("SELECT EMSensorStrength, PassiveSensorStrength  FROM FCT_ShipClass WHERE ShipClassID = ?", (new_class_id,))[0])
                em = max(item[0] for item in sensor_data)
                th = max(item[1] for item in sensor_data)
                list_system_objects.append(PlayerFleet(row[1], row[3], row[4], "", row[2], em, th, f"{', '.join(ships)}"))
            except (ValueError, IndexError): #to handle fleets with no ships
                list_system_objects.append(PlayerFleet(row[1], row[3], row[4], "", 0, 0, 0, "no ships in fleet"))
        #load player missiles
        list_system_objects +=[PlayerMissileSalvo(f"Missile Salvo of {row[6]} missiles", row[3], row[4], "", row[5], row[7]) for row in self.execute("""SELECT MissileSalvoID, TargetType, TargetID, xcor, ycor, MissileSpeed, Name,
                                    COUNT(FCT_Missile.SalvoID) as MissileCount,
            FROM FCT_MissileSalvo
            JOIN FCT_MissileType ON FCT_MissileSalvo.MissileID = FCT_MissileType.MissileID
            JOIN FCT_missile on FCT_MissileSalvo.MissileSalvoID = FCT_missile.SalvoID
            WHERE FCT_MissileSalvo.GameID = ? AND FCT_MissileSalvo.RaceID = ? AND FCT_MissileSalvo.SystemID = ?
            GROUP BY FCT_MissileSalvo.MissileSalvoID""", (game_id, race_id, system_id))]
        print(f"Loading complete. Loaded {len(list_system_objects)} objects in {round(time.time() - start_time, 2)} seconds")
        return list_system_objects
