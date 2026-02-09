import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the registered dataset from init_main_map_registration
file_path = '.\\DataCSV\\dataset_collisions.csv'
df = pd.read_csv(file_path)

print(f"Dataset loaded: {len(df)} registers detected.")

# Jam detection: if < 0.5 km/h during 2-3 seg
JAM_VELOCITY = 0.5
REGISTERS_WINDOW = 10

print("Analysing jams and collisions...")

# 1 if vehicle is jammed
df['is_stuck'] = df.groupby('v_id')['speed_kmh'].transform(
    lambda x: x.rolling(window=REGISTERS_WINDOW).max() < JAM_VELOCITY
).fillna(0).astype(int)

df['incident_detected'] = ((df['collision'] == 1) | (df['is_stuck'] == 1)).astype(int)

# 2. Data cleaning to analyse movements
df_active = df[df['speed_kmh'] > 0.1].copy()

# 3. Feature Engineering
# Velocity variation
df_active['delta_speed'] = df_active.groupby('v_id')['speed_kmh'].diff()

# 4. Analysis
total_collisions = df['collision'].sum()
total_stuck_events = df['is_stuck'].sum()
print(f"--- Incidents ---")
print(f"Total of physical crashes: {total_collisions}")
print(f"Total of vehicles jammed: {total_stuck_events}")
print(f"-----------------------------")

# 5. Visualization - Added 'incident_detected' to see results
plt.figure(figsize=(10, 8))
cols_to_corr = ['speed_kmh', 'throttle', 'brake', 'steer', 'delta_speed', 'collision', 'is_stuck', 'incident_detected']
sns.heatmap(df_active[cols_to_corr].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix: Baronissi Traffic Analysis')
plt.show()

# 6. Velocity distribution vs Total incidents
plt.figure(figsize=(10, 5))
sns.kdeplot(data=df_active, x='speed_kmh', hue='incident_detected', fill=True, common_norm=False)
plt.title('Velocity distribution: Normal Flow vs Incidents (Crashes/Jamms)')
plt.xlabel('Velocity (km/h)')
plt.ylabel('Registers (density)')
plt.grid(alpha=0.3)
plt.show()

# 7. Identify strong stops (likely to be crashes) - If velocity was abruptly reducted more than 10 km/h
hard_braking = df_active[df_active['delta_speed'] < -10]
print(f"Detected abruptive stops: {len(hard_braking)}")

# 8. Saved dataset to use it for AI training
df.to_csv('.\\DataCSV\\dataset_vehicles_enriched.csv', index=False)
print("Dataset with incidents saved.")