import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

FILE_PATH = '.\\DataCSV\\dataset_collisions.csv'
ENRICHED_FILE = '.\\DataCSV\\dataset_vehicles_enriched.csv'
JAM_VELOCITY = 0.5    
REGISTERS_WINDOW = 10 
PROXIMITY_THRESHOLD = 15.0

if not os.path.exists(FILE_PATH):
    print(f"Error: {FILE_PATH} not found.")
    exit()

df = pd.read_csv(FILE_PATH)
print(f"Dataset loaded: {len(df)} registers detected.")

print("Analyzing jams and collisions...")
df['is_stuck'] = df.groupby('v_id')['speed_kmh'].transform(
    lambda x: x.rolling(window=REGISTERS_WINDOW).max() < JAM_VELOCITY
).fillna(0).astype(int)

accident_spots = df[df['collision'] == 1][['x', 'y']].drop_duplicates()

def check_jam_cause(row, accidents, threshold):
    """
    Checks if a stuck vehicle is near a recorded accident.
    Returns 1 if it's a 'Jam by Crash', 0 otherwise.
    """
    if row['is_stuck'] == 0: return 0
    if row['collision'] == 1: return 0 
    
    # Calculate Euclidean distance to every accident spot
    for _, acc in accidents.iterrows():
        dist = np.sqrt((row['x'] - acc['x'])**2 + (row['y'] - acc['y'])**2)
        if dist < threshold:
            return 1
    return 0

if not accident_spots.empty:
    df['jam_by_crash'] = df.apply(lambda r: check_jam_cause(r, accident_spots, PROXIMITY_THRESHOLD), axis=1)
else:
    df['jam_by_crash'] = 0

# 'normal' traffic jams 
df['jam_normal'] = ((df['is_stuck'] == 1) & (df['jam_by_crash'] == 0) & (df['collision'] == 0)).astype(int)

df['incident_detected'] = ((df['collision'] == 1) | (df['is_stuck'] == 1)).astype(int)

df_active = df[df['speed_kmh'] > 0.1].copy()
df_active['delta_speed'] = df_active.groupby('v_id')['speed_kmh'].diff()

unique_crashes = df[df['collision'] == 1]['v_id'].nunique()
print("\n" + "="*30)
print(f"INCIDENT SUMMARY")
print(f"="*30)
print(f"Unique vehicles involved in crashes: {unique_crashes}")
print(f"Normal traffic jam registers: {df['jam_normal'].sum()}")
print(f"Accident-related jam registers: {df['jam_by_crash'].sum()}")
print(f"Hard braking events detected (>10km/h drop): {len(df_active[df_active['delta_speed'] < -10])}")
print("="*30)

# Graph 1: Spatial Incident Map (X/Y Coordinates)
plt.figure(figsize=(12, 8))
plt.scatter(df['x'], df['y'], c='lightgrey', s=1, alpha=0.1, label='Normal Flow')
plt.scatter(df[df['jam_normal']==1]['x'], df[df['jam_normal']==1]['y'], c='orange', s=5, label='Traffic Jam')
plt.scatter(df[df['jam_by_crash']==1]['x'], df[df['jam_by_crash']==1]['y'], c='red', s=10, label='Jam by Crash')
plt.scatter(accident_spots['x'], accident_spots['y'], c='black', marker='X', s=100, label='Collision Points')

plt.title('Spatial Incident Analysis: Baronissi Map')
plt.xlabel('X Coordinates')
plt.ylabel('Y Coordinates')
plt.legend()
plt.grid(True, alpha=0.2)
plt.show()

# Graph 2: Feature Correlation Heatmap
plt.figure(figsize=(10, 8))
cols_to_corr = ['speed_kmh', 'throttle', 'brake', 'steer', 'delta_speed', 'collision', 'jam_normal', 'jam_by_crash']
sns.heatmap(df_active[cols_to_corr].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Feature Correlation Matrix')
plt.show()

df.to_csv(ENRICHED_FILE, index=False)
print(f"\nEnriched dataset saved at: {ENRICHED_FILE}")