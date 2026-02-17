import carla
import math
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import init_main_map as map_tool
import random

try:
    model = joblib.load('traffic_aimodel.pkl')
    print("AI Model loaded")
except:
    print("Couldn't found AI Model'")
    exit()

def asses_risk(v, ai_model):
    vel = v.get_velocity()
    speed = 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
    control = v.get_control()  
    input_df = pd.DataFrame([[speed, control.throttle, control.brake, control.steer]], 
                            columns=['speed_kmh', 'throttle', 'brake', 'steer'])   
    return ai_model.predict(input_df)[0]


client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = map_tool.initialize_world(client)
#map_tool.set_bad_weather(world)
#map_tool.spawn_pedestrians(client, world, 50)
map_tool.center_camera(world)
tm = client.get_trafficmanager(8000)
tm.set_global_distance_to_leading_vehicle(1.5)
bp_library = world.get_blueprint_library()
blueprints = bp_library.filter('vehicle.*')
collision_bp = bp_library.find('sensor.other.collision')

spawn_points = world.get_map().get_spawn_points()
random.shuffle(spawn_points)

for i in range(min(45, len(spawn_points))):
    bp = random.choice(blueprints)
    vehicle = world.try_spawn_actor(bp, spawn_points[i])
    if vehicle:
        vehicle.set_autopilot(True, 8000)
        tm.vehicle_percentage_speed_difference(vehicle, 30.0)

debug = world.debug
risk_detected_vehicles = set()

print("AI monitoring risks...")

try:
    while True:
        world.wait_for_tick()
        vehiculos = world.get_actors().filter('vehicle.*')
        
        for v in vehiculos:
            risk = asses_risk(v, model)           
            # If risk detected, show a visual alert
            if risk == 1:
                loc = v.get_transform().location
                debug.draw_arrow(loc + carla.Location(z=5), loc + carla.Location(z=2), 
                                 thickness=0.2, arrow_size=0.3, 
                                 color=carla.Color(255, 0, 0), life_time=0.1)
                if v.id not in risk_detected_vehicles:
                    risk_detected_vehicles.add(v.id)
                    print(f"AI ALERT: Possible incident in vehicle {v.id}")
            elif risk == 0 and v.id in risk_detected_vehicles:
                risk_detected_vehicles.remove(v.id)

except KeyboardInterrupt:
    print("\nAI analysis stopped.")