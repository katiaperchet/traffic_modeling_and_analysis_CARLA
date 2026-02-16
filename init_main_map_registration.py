import carla
import time
import math
import random
import pandas as pd
import os
import init_main_map as map_tool  

OUTPUT_FILE = '.\\DataCSV\\dataset_collisions.csv'
DURATION_SIM = 180
NUM_VEHICLES = 45
collisions_registered = {}
collisioned_vehicles= set()

def collision_callback(event, dict_collisions):

    if event.actor.id not in collisioned_vehicles:
        actor = event.actor
        dict_collisions[event.actor.id] = True
        actor.set_autopilot(False)
        control = carla.VehicleControl()
        control.steer = 0.0
        control.throttle = 0.0
        control.brake = 1.0
        control.hand_brake = True
        actor.apply_control(control)
        collisioned_vehicles.add(event.actor.id)
        print(f"Vehicle {actor.id} crashed and stopped")

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(60.0)

    vehicles_list = []
    sensors_list = []
    data_log = []

    try:
        world = map_tool.initialize_world(client)
        map_tool.center_camera(world)
        tm = client.get_trafficmanager(8000)
        tm.set_global_distance_to_leading_vehicle(1.5)

        bp_library = world.get_blueprint_library()
        blueprints = bp_library.filter('vehicle.*')
        collision_bp = bp_library.find('sensor.other.collision')

        spawn_points = world.get_map().get_spawn_points()
        random.shuffle(spawn_points)
        print(f"Spawning {NUM_VEHICLES} vehicles with collision sensors...")

        for i in range(min(NUM_VEHICLES, len(spawn_points))):
            bp = random.choice(blueprints)
            vehicle = world.try_spawn_actor(bp, spawn_points[i])

            if vehicle:
                vehicle.set_autopilot(True, 8000)
                tm.vehicle_percentage_speed_difference(vehicle, 30.0)
                vehicles_list.append(vehicle)
                col_sensor = world.spawn_actor(collision_bp, carla.Transform(), attach_to=vehicle)
                col_sensor.listen(lambda event, v_id=vehicle.id: collision_callback(event, collisions_registered))
                sensors_list.append(col_sensor)
        print(f"Recording started. Duration: {DURATION_SIM}s")

        start_time = time.time()
        sampling_interval= 0.5
        last_record_time=0

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > DURATION_SIM:
                break
            world.wait_for_tick()

            if elapsed_time - last_record_time >= sampling_interval:
                for v in vehicles_list:
                    if v.is_alive:
                        transform = v.get_transform()
                        loc = transform.location

                        if loc.z < -0.5:
                            waypoint = world.get_map().get_waypoint(loc, project_to_road=True)
                            new_loc = waypoint.transform.location + carla.Location(z=1.0)
                            v.set_transform(carla.Transform(new_loc, waypoint.transform.rotation))
                            v.set_target_velocity(carla.Vector3D(0, 0, 0))
                            print(f"Vehicle {v.id} rescued from void.")
                        vel = v.get_velocity()
                        speed_kmh = 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
                        control = v.get_control()
                        collision_detected = 1 if v.id in collisions_registered else 0
                        data_log.append({
                            'timestamp': elapsed_time,
                            'v_id': v.id,
                            'x': loc.x,
                            'y': loc.y,
                            'speed_kmh': speed_kmh,
                            'throttle': control.throttle,
                            'brake': control.brake,
                            'steer': control.steer,
                            'collision': collision_detected
                        })
                last_record_time = elapsed_time
                collisions_registered.clear()
        print("Simulation finished. Saving data...")
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        df = pd.DataFrame(data_log)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Data successfully saved in {OUTPUT_FILE}")
    except Exception as e:
        print(f"Critical error during recording: {e}")
    finally:
        print("Cleaning up actors...")
        for s in sensors_list:
            if s.is_alive:
                s.destroy()
        client.apply_batch([carla.command.DestroyActor(x.id) for x in vehicles_list])
        print("Cleanup complete.")
if __name__ == "__main__":
    main()