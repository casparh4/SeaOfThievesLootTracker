from flask import Flask, request, render_template
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import data_access
import datetime
import os
import json
# Flask is a lightweight WSGI web application framework in Python designed to make building web applications and APIs quick and flexible. It’s called a microframework because it provides only the core essentials—routing, request handling, and templating—while leaving other choices like database integration or authentication to the developer.


global_players = []
global_loot = data_access.load_loot()
global_locations = data_access.load_locations()


logged_in_player =[]
past_coords = []


# config app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#SQLALCHEMY_DATABASE_URI: Specifies the database location (SQLite in this case).
#SQLALCHEMY_TRACK_MODIFICATIONS: Disables unnecessary change tracking for better performance.

#create a path to where the db will be stored
try:
    os.makedirs(app.instance_path)
except OSError:
    pass
# create the database object
db = SQLAlchemy(app)

# define a model, which represents a table in the db
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.now)

# create the database tables
with app.app_context():
    db.create_all()
# ensures all models are created in the database before the application starts handling requests.


#creating an event instance and adding it to the database
def add_event(event_description):
    new_event = Event(event=event_description)
    db.session.add(new_event)
    db.session.commit()





@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in_player
    global global_players
    
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        global_players = data_access.load_players()

        for player in global_players:
            if player.name == name and player.password == password:
                print(f"Player {name} logged in successfully.")
                logged_in_player = player
                break
            else:
                print(f"Login failed for player {name}.")
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    
    global logged_in_player # define logged_in_player as a global variable to access it within the function
    global past_coords
    nav = None  # Initialize nav to None at the start of the function

    print(logged_in_player.name, logged_in_player.password, logged_in_player.found_loot)  # Debugging line to check the value of logged_in_player
    if request.method == 'POST' and request.form.get("form_id") == "enter_coord":
        return navigation()
    elif(request.method == 'POST' and request.form.get("form_id") == "add_loot"):
        return add_loot()
    elif (request.method == 'POST' and request.form.get("form_id") == "sell_loot"):
        total_loot_value = sum(loot.loot.value for loot in logged_in_player.found_loot)
        logged_in_player.earnings += total_loot_value
        logged_in_player.found_loot.clear()

        return render_template('home.html', logged_in_player=logged_in_player, past_coords=past_coords, stats = getPlayerStats())

    return render_template('home.html', logged_in_player=logged_in_player, past_coords=past_coords, stats = getPlayerStats())




def add_loot():
    global logged_in_player
    global global_loot
    global past_coords
    global_locations

    if request.method == 'POST':
        location_suggestions = None
        loot_suggestions = None
        input_loot_name = request.form.get("loot_name")
        
        input_location = request.form.get("loot_location")

        loot = next((loot for loot in global_loot if loot.name.lower() == input_loot_name.lower()), None)
        location = next((location for location in global_locations if location.name.lower() == input_location.lower()), None)
        loot_and_location = data_access.player_loot(loot, location)
        logged_in_player.found_loot.append(loot_and_location)

        if(loot and location):
            return render_template('home.html', logged_in_player=logged_in_player, past_coords=past_coords, stats = getPlayerStats() )
        else:
            loot_suggestions = [loot for loot in global_loot if input_loot_name.lower() in loot.name.lower()]
            location_suggestions = [location for location in global_locations if input_location.lower() in location.name.lower()]
        return render_template('home.html', logged_in_player=logged_in_player, past_coords=past_coords, location_suggestions = location_suggestions, loot_suggestions = loot_suggestions, stats = getPlayerStats() )
        
def getPlayerStats():

    global logged_in_player
    most_valuable_loot = max(logged_in_player.found_loot, key=lambda loot: loot.loot.value, default=None)
    most_common_loot = max(set(logged_in_player.found_loot), key=lambda loot: logged_in_player.found_loot.count(loot), default=None)
    most_successful_location = max(set(loot.location.name for loot in logged_in_player.found_loot), key=lambda loc: sum(1 for loot in logged_in_player.found_loot if loot.location.name == loc), default=None)
    stats = data_access.PLayer_stats(logged_in_player, most_valuable_loot, most_common_loot, most_successful_location)

    return stats

def navigation():
    global past_coords
    player_coordinate = request.form.get("coord")
    past_coords.append(player_coordinate)

    with open('jsonData/grid.json', 'r') as file:
        coords_and_locations = json.load(file)

    readable_coord = player_coordinate[0] + "-" + player_coordinate[1:3]
    location = coords_and_locations[readable_coord]
    coord_letter, coord_number = player_coordinate[0], player_coordinate[1:3]
    if location:
        print(f"You are at {location}.")
    north = coords_and_locations.get(f"{coord_letter}-{int(coord_number) - 1}")
    south = coords_and_locations.get(f"{coord_letter}-{int(coord_number) + 1}")
    east = coords_and_locations.get(f"{chr(ord(coord_letter) + 1)}-{coord_number}")
    west = coords_and_locations.get(f"{chr(ord(coord_letter) - 1)}-{coord_number}")

    nav = data_access.Navigation(location, north, south, east, west)
    return render_template(
        'home.html',
        logged_in_player=logged_in_player,
        player_coordinate=player_coordinate,
        past_coords=past_coords,
        nav=nav,
        stats=getPlayerStats(),
    )






if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
    

