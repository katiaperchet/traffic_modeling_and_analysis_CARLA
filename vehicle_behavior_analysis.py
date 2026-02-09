import carla
import math
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

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
world = client.get_world()
debug = world.debug

# --- REAL TIME PREDICTION ---
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
                debug.draw_arrow(loc + carla.Location(z=2), loc + carla.Location(z=5), 
                                 thickness=0.2, arrow_size=0.3, 
                                 color=carla.Color(255, 0, 0), life_time=0.1)
                print(f"AI ALERT: Possible incident in vehicle {v.id}")

except KeyboardInterrupt:
    print("\nAI analysis stopped.")