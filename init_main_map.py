import carla
import time
import random

XODR_PATH = ".\\baronissi_base_map.xodr"
NUM_VEHICLES = 45 

def setup_environment(world):
    print("Setting up safety ground...")
    bp_lib = world.get_blueprint_library()
    ground_bp = bp_lib.filter('static.prop.platform*')[0]
    spawn_points = world.get_map().get_spawn_points()
    
    for i in range(0, len(spawn_points), 100):
        p = spawn_points[i]
        t = carla.Transform(p.location + carla.Location(z=-0.5), p.rotation)      
        ground = world.try_spawn_actor(ground_bp, t)
        if ground:
            ground.set_simulate_physics(False)
    print("Environment Ready.")

client = carla.Client('localhost', 2000)
client.set_timeout(60.0) 

try:
    print("Loading Baronissi...")
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
    for i in range(min(NUM_VEHICLES, len(spawn_points))):
        bp = random.choice(blueprints)
        v = world.try_spawn_actor(bp, spawn_points[i])
        if v:
            v.set_autopilot(True, 8000)
            tm.vehicle_percentage_speed_difference(v, 30.0)
            vehicles_list.append(v)

    print(f"Server ready with {len(vehicles_list)} vehicles. Press Ctrl+C to stop.")
    
    while True:
        world.wait_for_tick()
        
except Exception as e:
    print(f"Error: {e}")