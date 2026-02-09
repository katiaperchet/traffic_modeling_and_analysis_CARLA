# Thesis on Traffic Modeling and Analysis using CARLA Simulation

## Information
#### Replication, modeling and predictive analysis for urban roads, focusing on the city of Baronissi as a case of study. The project involves: scenario virtualization, behavioral data research, predictive AI modeling and real-time behavior analysis. 

## Project File Structure:
1. main_map_conversion.py - transforms geographic data extracted from OSM into XODR format, needed for CARLA Simulator.
2. init_main_map.py - loads the map into the simulator and handles traffic spawning.
3. init_main_map_registration.py - loads the map into the simulator, handles traffic spawning and records its behavior for CSV creation.
4. world_data_analysis.py - analyses information captured in file #3 to create a correlation matrix, velocity distribution and creates CSV for AI training
5. mlmodel_training.py - trains the Random Forest and exports the .pkl model
6. vehicle_behavior_analysis.py - performs live behavior analysis and risk detection. 
## Steps
1. Download .osm map
2. Execute main_map_conversion.py to transform .osm into .xodr
3. Execute init_main_map_registration.py to capture vehicles' data
4. Execute world_data_analysis.py to detect collisions or incidents and create an enriched .csv
5. Execute mlmodel_training.py to train a Random Forest with the captured data
6. Execute init_main_map.py to upload map for risk assesment
7. Execute vehicle_behavior_analysis.py to see risk assesment

