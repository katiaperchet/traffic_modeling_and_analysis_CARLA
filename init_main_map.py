import carla
import time
import random

XODR_PATH = ".\\baronissi_base_map.xodr"
NUM_VEHICLES_DEFAULT = 45 

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

def center_camera(world):
    spectator = world.get_spectator()
    spawn_points = world.get_map().get_spawn_points()
    if spawn_points:
        center_x = sum(p.location.x for p in spawn_points) / len(spawn_points)
        center_y = sum(p.location.y for p in spawn_points) / len(spawn_points)
        center_location = carla.Location(x=center_x, y=center_y, z=100.0)
        center_rotation = carla.Rotation(pitch=-90, yaw=0, roll=0)
        spectator.set_transform(carla.Transform(center_location, center_rotation))
        print(f"Camera centered at: {center_x:.2f}, {center_y:.2f}")

def initialize_world(client):
    print("Loading Baronissi...")
    with open(XODR_PATH, 'r', encoding='latin-1') as f:
        xodr_xml = f.read()
    
    world = client.generate_opendrive_world(xodr_xml, carla.OpendriveGenerationParameters(
        vertex_distance=2.0, max_road_length=50.0, wall_height=0.0,
        additional_width=0.6, smooth_junctions=True, enable_mesh_visibility=True))
    
    time.sleep(2.0)
    setup_environment(world)
    return world

if __name__ == "__main__":
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(60.0)
        world = initialize_world(client)
        center_camera(world)
        
        blueprints = world.get_blueprint_library().filter('vehicle.*')
        spawn_points = world.get_map().get_spawn_points()
        random.shuffle(spawn_points)
        
        for i in range(min(NUM_VEHICLES_DEFAULT, len(spawn_points))):
            v = world.try_spawn_actor(random.choice(blueprints), spawn_points[i])
            if v: v.set_autopilot(True)
            
        print("Running standalone. Press Ctrl+C to stop.")
        while True:
            world.wait_for_tick()
            
    except Exception as e:
        print(f"Error in standalone: {e}")