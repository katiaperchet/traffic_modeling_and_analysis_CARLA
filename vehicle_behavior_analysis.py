import carla
import math
import numpy as np
import joblib
import pandas as pd
import init_main_map as map_tool 
import random

TARGET_VEHICLE_COUNT = 80  
SPAWN_TICK_INTERVAL = 30   
tick_counter = 0

try:
    model = joblib.load('traffic_aimodel.pkl')
    print("AI Model loaded")
except:
    print("Couldn't find AI Model")
    exit()

def asses_risk(v, ai_model):
    try:
        vel = v.get_velocity()
        speed = 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
        control = v.get_control()  
        input_df = pd.DataFrame([[speed, control.throttle, control.brake, control.steer]], 
                                columns=['speed_kmh', 'throttle', 'brake', 'steer'])   
        return ai_model.predict(input_df)[0]
    except:
        return 0

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = map_tool.initialize_world(client) 
map_tool.center_camera(world)             

# map_tool.set_bad_weather(world)
# map_tool.spawn_pedestrians(client, world, 30)

tm = client.get_trafficmanager(8000)
tm.set_global_distance_to_leading_vehicle(1.5)

bp_library = world.get_blueprint_library()
blueprints = bp_library.filter('vehicle.*')
spawn_points = world.get_map().get_spawn_points()
random.shuffle(spawn_points)

debug = world.debug
risk_detected_vehicles = set()

print(f"AI Monitoring + Dynamic Spawning (Target: {TARGET_VEHICLE_COUNT})")

try:
    while True:
        world.wait_for_tick()
        tick_counter += 1
        
        current_vehicles = world.get_actors().filter('vehicle.*')
        active_list = [v for v in current_vehicles if v.is_alive]
        
        if len(active_list) < TARGET_VEHICLE_COUNT and tick_counter >= SPAWN_TICK_INTERVAL:
            tick_counter = 0
            bp = random.choice(blueprints)
            sp = random.choice(spawn_points)
            vehicle = world.try_spawn_actor(bp, sp)
            
            if vehicle:
                vehicle.set_autopilot(True, 8000)
                tm.vehicle_percentage_speed_difference(vehicle, 30.0)
                p = vehicle.get_physics_control()
                p.center_of_mass = carla.Vector3D(0, 0, -2.0)
                vehicle.apply_physics_control(p)
                print(f"Traffic increasing: {len(active_list) + 1}/{TARGET_VEHICLE_COUNT}")

        for v in active_list:
            try:
                risk = asses_risk(v, model)
                nearby_vehicles = [x for x in active_list if x.id != v.id and 
                       x.get_location().distance(v.get_location()) < 15.0]           
                if risk == 1 and len(nearby_vehicles) > 0:
                    loc = v.get_transform().location
                    debug.draw_arrow(loc + carla.Location(z=5), loc + carla.Location(z=2), 
                                     thickness=0.2, arrow_size=0.3, 
                                     color=carla.Color(255, 0, 0), life_time=0.1)
                    if v.id not in risk_detected_vehicles:
                        risk_detected_vehicles.add(v.id)
                        print(f"AI ALERT: Incident risk in vehicle {v.id}")
                elif risk == 0 and v.id in risk_detected_vehicles:
                    risk_detected_vehicles.remove(v.id)
            except:
                continue

except KeyboardInterrupt:
    print("\nSimulation stopped by user.")