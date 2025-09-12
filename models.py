from dataclasses import dataclass
from typing import Any
# Base class for all game objects with position and description
@dataclass
class BaseSystemObject:
    name: str          # Name of the object
    x: float           # X coordinate
    y: float           # Y coordinate
    miscellaneous_data: str  # Additional information
    object_type: str #contains exactly what an object is, for example, lifepod, missile salvo for filtering.
    def __post_init__(self):
        #makes sure all fields are correct
        if type(self.x) == float:
            self.x = round(self.x)
        if type(self.y) == float:
            self.y = round(self.y)
    def __str__(self):
        # String representation with or without miscellaneous data
        if self.miscellaneous_data == "":
            return f"{self.name}"
        return f"{self.name} {self.miscellaneous_data}."
    def __iter__(self):
        #returns a tuple with position data for checking distance etc
        return iter((self.x, self.y))

@dataclass
class BaseBody(BaseSystemObject):
    minerals: dict
    def __str__(self):
        view_minerals =[(mineral, round(data[0]), data[1]) for mineral, data in self.minerals.items() if data[0] > 0]
        if len(view_minerals) > 0:
            return f"{self.name} minerals {view_minerals}"
        return f" {self.name}"
# Class for NPR colonies
@dataclass
class NPRPop(BaseSystemObject):
    em: int ## Electromagnetic signature
    th: int # Thermal signature
    def __str__(self):
        # String representation including EM and thermal signatures
        return f"{self.name} EM signature: {self.em} thermal signature: {self.th},"

# Class for player populations with detection strength and population size
@dataclass
class PlayerPop(BaseSystemObject):
    dsp_strength: int #Deep space tracking station strength
    population: float #Population in millions
    def __str__(self):
        return f"{self.name} Population: {self.population} million"

#class for player fleets
@dataclass
class PlayerFleet(BaseSystemObject):
    speed: int #speed of the fleet (in km)
    em_detecction: int #max EM sensor sensativity
    th_detection: int #max thermal sensor sensativity
    #detection range = (0.25 * sqrt(Sensor Sensitivity) * sqrt(detected signal strength) * 1000000
    ships: str #list of names of ships in class.
    def __str__(self):
        return f"Fleet {self.name} with ships {self.ships}, at speed {self.speed}, "

@dataclass
class NonPlayerFleet(BaseSystemObject):
    speed: int
    ships: str
    def __str__(self):
        return f"NPR fleet with ships {self.ships}, at a speed of {self.speed}KM/s"
@dataclass
class MissileSalvo(BaseSystemObject):
    speed: int
    num_missiles: int #aont of missiles i the salvo
    def __str__(self):
        return f"{self.name}, with {self.num_missiles} missiles, speed {self.speed}KM/s"
@dataclass
class ProximityObject:
    """Gives objects an angle and distance value"""
    object: Any
    distance: int
    bearing: int
    def __str__(self):
        return f"{self.object} distance, {self.distance}km, bearing {self.bearing}degrees"
