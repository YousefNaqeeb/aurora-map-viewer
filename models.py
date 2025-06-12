from dataclasses import dataclass

# Base class for all game objects with position and description
@dataclass
class BaseSystemObject:
    name: str          # Name of the object
    x: float           # X coordinate
    y: float           # Y coordinate
    miscellaneous_data: str  # Additional information
    def __post_init__(self):
        #makes sure all fields are correct
        if type(self.x) == float:
            self.x = round(self.x)
        if type(self.y) == float:
            self.y = round(self.y)
    def __str__(self):
        # String representation with or without miscellaneous data
        if self.miscellaneous_data == "":
            return f"name: {self.name} position: {self.x}, {self.y}."
        return f"{self.name} position: {self.x}, {self.y} {self.miscellaneous_data}."
    def __iter__(self):
        #returns a tuple with position data for checking distance etc
        return iter((self.x, self.y))
# Class for objects with electromagnetic and thermal signatures
@dataclass
class BaseDetectableObject(BaseSystemObject):
    em: int ## Electromagnetic signature
    th: int # Thermal signature
    def __str__(self):
        # String representation including EM and thermal signatures
        if self.miscellaneous_data == "":
            return f"{self.name} EM signature: {self.em} thermal signature: {self.th}position: {self.x}, {self.y}."
        return f"{self.name} EM signature: {self.em} thermal signature: {self.th} position: {self.x}, {self.y} {self.miscellaneous_data}."

# Class for player populations with detection strength and population size
@dataclass
class PlayerPop(BaseSystemObject):
    dsp_strength: int #Deep space tracking station strength
    population: float #Population in millions
    def __str__(self):
        return f"{self.name} Population: {self.population} million, position: {self.x}, {self.y}."

#class for player fleets
@dataclass
class PlayerFleet(BaseSystemObject):
    speed: int #speed of the fleet (in km)
    em_detecction: int #max EM sensor sensativity
    th_detection: int #max thermal sensor sensativity
    #detection range = (0.25 * sqrt(Sensor Sensitivity) * sqrt(detected signal strength) * 1000000
    ships: str #list of names of ships in class.
    def __str__(self):
        return f"Fleet {self.name} with ships {self.ships}, at speed {self.speed}, position: {self.x}, {self.y}."

@dataclass
class NonPlayerFleet(BaseSystemObject):
    speed: int
    ships: str
    def __str__(self):
        return f"NPR fleet with ships {self.ships}, at a speed of {self.speed}KM/s, at position: {self.x}, {self.y}"
@dataclass
class MissileSalvo(BaseSystemObject):
    speed: int
    num_missiles: int #aont of missiles i the salvo
    def __str__(self):
        return f"{self.name}, with {self.num_missiles} missiles, speed {self.speed}KM/s at position: {self.x}, {self.y}"
