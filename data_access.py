import json
import jsonData

class Loot:
  def __init__(self, name, type, value):
    self.name = name
    self.type = type
    self.value = value

  def to_dict(self):
    return {
        "name": self.name,
        "type": self.type,
        "value": self.value
      }
  @classmethod
  def from_dict(cls, data):
      name = data.get('name')
      type = data.get('type')
      value = data.get('value')
      return cls(name, type, value)

class player_loot:
  def __init__(self, loot, location):
    self.loot = loot
    self.location = location

  def to_dict(self):
    return {
      "loot": self.loot.to_dict() if self.loot else None,
      "location": self.location.to_dict() if self.location else None
    }

  @classmethod
  def from_dict(cls, data):
      if data is None:
          return None
      loot = Loot.from_dict(data.get('loot')) if data.get('loot') else None
      location = Location.from_dict(data.get('location')) if data.get('location') else None
      return cls(loot, location)

class Player:
 def __init__(self, name, password, found_loot, earnings=0):
  self.name = name
  self.password = password
  self.found_loot = found_loot
  self.earnings = earnings

 def add_loot(self, player_loot):
  self.found_loot.append(player_loot)

 def to_dict(self):
   return {
            "name": self.name,
            "password": self.password,
            "found_loot": [loot.to_dict() for loot in self.found_loot if loot is not None],
            "earnings": self.earnings
            
  }

class PLayer_stats:
   def __init__(self,player, most_valuable_loot, most_common_loot, most_successful_location):
      self.player = player
      self.most_valuable_loot = most_valuable_loot
      self.most_common_loot = most_common_loot
      self.most_successful_location = most_successful_location

class Location:
 def __init__(self, name, type, grid, region):
  self.name = name
  self.coordinate = grid
  self.type = type
  self.region = region

 def to_dict(self):
    return {
      "name": self.name,
      "type": self.type,
      "grid": self.coordinate,
      "region": self.region
    }
 @classmethod
 def from_dict(cls, data):
     name = data.get('name')
     type = data.get('type')
     grid = data.get('grid')
     region = data.get('region')
     return cls(name, type, grid, region)

class Navigation:
   def __init__(self, nearby, north, south, east, west):
       self.nearby = nearby
       self.north = north
       self.south = south
       self.east = east
       self.west = west



def load_players():
   with open('jsonData/players.json', 'r') as file:
        data = json.load(file)
        players = []
        try:
            players = [Player(player_data['name'], player_data['password'], [player_loot.from_dict(loot) for loot in player_data.get('found_loot', [])]) for player_data in data]
        except json.JSONDecodeError:
            players = []
        print(f"Loaded players: {[player.name for player in players]}")  # Debugging line
        return players

def load_loot():
    with open('jsonData/all_loot.json', 'r') as file:
        data = json.load(file)
        loot_list = []
        try:
            loot_list = [Loot(loot_data['name'], loot_data['type'], loot_data['value']) for loot_data in data]
        except json.JSONDecodeError:
            loot_list = []
        print(f"Loaded loot: {[loot.name for loot in loot_list]}")  # Debugging line
        return loot_list

def load_locations():
    with open('jsonData/locations.json', 'r') as file:
        data = json.load(file)
        locations = []
        try:
            locations = [Location(location_data['name'], location_data['type'], location_data['grid'], location_data['region']) for location_data in data]
        except json.JSONDecodeError:
            locations = []
        print(f"Loaded locations: {[location.name for location in locations]}")  # Debugging line
        return locations
    

def save_players(players):
    with open('jsonData/players.json', 'w') as file:
        json.dump([player.to_dict() for player in players], file, indent=4)
   
        
          
          
   

