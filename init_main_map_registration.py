import carla
import time
import random
import pandas as pd
import math

XODR_PATH = ".\\baronissi_base_map.xodr"
OUTPUT_FILE = '.\\DataCSV\\dataset_collisions.csv'
NUM_VEHICLES = 45 
DURATION_SIM = 180 

collisions_registered = {}

def collision_callback(event, dict_collisions):
    dict_collisions[event.actor.id] = True

def setup_environment(world):
    print("Safety ground to have a large coverage and avoid vehicles into void...")
    bp_lib = world.get_blueprint_library()
    
    ground_bp = bp_lib.filter('static.prop.platform*')[0]
    
    spawn_points = world.get_map().get_spawn_points()
    
    for i in range(0, len(spawn_points), 100):
        p = spawn_points[i]
        t = carla.Transform(p.location + carla.Location(z=-0.5), p.rotation)      
        ground = world.try_spawn_actor(ground_bp, t)
        
        if ground:
            ground.set_simulate_physics(False)
            ground.set_transform(carla.Transform(
                t.location, 
                t.rotation
            ))
            
    print("Safety net displayed.")

client = carla.Client('localhost', 2000)
client.set_timeout(60.0) 

try:
    print("Loading Baronissi's map...")
    with open(XODR_PATH, 'r', encoding='latin-1') as f:
        xodr_xml = f.read()
    world = client.generate_opendrive_world(xodr_xml, carla.OpendriveGenerationParameters(
        vertex_distance=2.0, max_road_length=50.0, wall_height=0.0,
        additional_width=0.6, smooth_junctions=True, enable_mesh_visibility=True))
    time.sleep(2.0)
    
    setup_environment(world)
    tm = client.get_trafficmanager(8000)
    tm.set_global_distance_to_leading_vehicle(1.5)

    blueprints = world.get_blueprint_library().filter('vehicle.*')
    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)

    vehicles_list = []
    sensors_list = []
    
    print(f"Spawning {NUM_VEHICLES} vehicles...")
    collision_bp = world.get_blueprint_library().find('sensor.other.collision')

    for i in range(min(NUM_VEHICLES, len(spawn_points))):
        bp = random.choice(blueprints)
        v = world.try_spawn_actor(bp, spawn_points[i])
        if v:
            v.set_autopilot(True, 8000)
            tm.vehicle_percentage_speed_difference(v, 30.0)
            vehicles_list.append(v)
            
            col_sensor = world.spawn_actor(collision_bp, carla.Transform(), attach_to=v)
            col_sensor.listen(lambda event, v_id=v.id: collision_callback(event, collisions_registered))
            sensors_list.append(col_sensor)

    print("Simulation on going...")
    data_log = []
    start_time = time.time()

    while time.time() - start_time < DURATION_SIM:
        world.wait_for_tick()
        timestamp = time.time() - start_time
        
        for v in vehicles_list:
            if v.is_alive:
                loc = v.get_transform().location

                # --- LOGIC TO AVOID VEHICLES FALL INTO VOID ---
                if loc.z < -0.5:
                    waypoint = world.get_map().get_waypoint(loc, project_to_road=True)
                    
                    # Position it a little bit in to avoid the falling (z=1.0)
                    new_loc = waypoint.transform.location + carla.Location(z=1.0)
                    new_rot = waypoint.transform.rotation
                    
                    v.set_transform(carla.Transform(new_loc, new_rot))
                    v.set_target_velocity(carla.Vector3D(0, 0, 0))
                    v.set_target_angular_velocity(carla.Vector3D(0, 0, 0))
                    
                    print(f"Saving vehicle {v.id} from falling into void...")

                vel = v.get_velocity()
                speed = 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
                control = v.get_control()
                chocó = 1 if v.id in collisions_registered else 0
                
                data_log.append({
                    'timestamp': timestamp, 'v_id': v.id,
                    'x': loc.x, 'y': loc.y, 'speed_kmh': speed,
                    'throttle': control.throttle, 'brake': control.brake,
                    'steer': control.steer, 'collision': chocó
                })
        collisions_registered.clear()

    print("Saving data and cleaning...")
    for s in sensors_list: s.destroy()
    client.apply_batch([carla.command.DestroyActor(x.id) for x in vehicles_list])
    
    pd.DataFrame(data_log).to_csv(OUTPUT_FILE, index=False)
    print(f"Data saved on {OUTPUT_FILE}")

except Exception as e:
    print(f"Se detuvo por: {e}")