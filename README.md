# Thesis on Traffic Modelling and Prediction of Hazardous Behaviours using CARLA Simulator and OpenStreetMap

This project implements a proactive framework for real-time traffic inference using CARLA Autonomous Driving simulator and Random forest machine learning model for prediction of hazardous behaviours. 


This repository is organized as a script-based pipeline:
1. Convert an OpenStreetMap extract into OpenDRIVE.
2. Record vehicle behaviour from a running CARLA scenario.
3. Enrich the recorded data by applying heuristic labels and merging them into a homogenous CSV file. 
4. Train a machine learning model (random forest classifier).
5. Run real-time inference on the Baronissi map.

## Prerequisites
You need a local Python environment with the libraries used directly by the scripts:
- `carla`
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `joblib`

You also need:
- CARLA Simulator `0.9.16`
- a local CARLA instance running on `localhost:2000`
- the repository files present in the root folder, especially `baronissi_base.osm` and `baronissi_base_map.xodr`

## CARLA 0.9.16 Setup

Reference release:
- `https://github.com/carla-simulator/carla/releases/tag/0.9.16`

Download the correct CARLA release package for your platform from that page:
- Ubuntu: `CARLA_0.9.16.tar.gz`
- Windows: `CARLA_0.9.16.zip`

Recommended setup:
1. download and extract CARLA `0.9.16`
2. launch the CARLA simulator locally
3. install the matching CARLA Python API from the extracted CARLA package
4. verify that the CARLA server is reachable on `localhost:2000`

Python API installation:
- after extracting CARLA, locate the wheel under `PythonAPI/carla/dist/`
- install the wheel that matches your Python version and operating system

Example pattern:

```bash
pip install /path/to/CARLA_0.9.16/PythonAPI/carla/dist/carla-<version>-<python>-<platform>.whl
```

Then install the remaining project dependencies.

## Repository Structure
Main Baronissi files:
- `main_map_conversion.py`: converts `baronissi_base.osm` into `baronissi_base_map.xodr`
- `init_main_map.py`: loads the Baronissi OpenDRIVE map into CARLA and provides helper functions used by the live analysis step
- `init_main_map_registration.py`: waits for active vehicles in the current CARLA world and records their state plus collision events into CSV files
- `world_data_analysis.py`: processes all recorded collision CSV files and generates the enriched master dataset
- `mlmodel_training.py`: trains the Random Forest classifier and saves `traffic_aimodel.pkl`
- `vehicle_behavior_analysis.py`: loads the trained model, recreates the Baronissi world, spawns traffic, and performs live risk inference

Separate Torino flow: do not mix the Torino scripts into the main workflow.
- `torino_map_conversion.py`
- `init_torino_sim.py`
- `torino_map.osm`
- `torino_traffic.xml`

## Step-By-Step Reproduction

### 1. Convert The Baronissi OSM Map

Input:
- `baronissi_base.osm`

Command:

```bash
python main_map_conversion.py
```

Output:
- `baronissi_base_map.xodr`

What it does:
- converts supported road types into OpenDRIVE using CARLA's `Osm2Odr`

### 2. Record Vehicle Behavior And Collisions

Command:

```bash
python init_main_map_registration.py
```

Output:
- a timestamped CSV in `DataCSV/` named like `dataset_collisions_YYYYMMDD_HHMMSS.csv`

What it records:
- timestamp
- vehicle id
- position `x`, `y`
- speed in km/h
- throttle
- brake
- steering
- collision flag

Runtime behavior:
- sampling interval: `0.5` seconds
- recording duration: `180` seconds
- collision sensors are attached to every detected vehicle

### 3. Build the Enriched Training Dataset

Command:

```bash
python world_data_analysis.py
```

Input:
- every file matching `DataCSV/dataset_collisions*.csv`

Output:
- `DataCSV/dataset_vehicles_enriched_MASTER.csv`

What it adds:
- stopped-traffic detection
- congestion near collision points
- derived incident labels for model training
- correlation visualization

Note:
- this script opens a Matplotlib window with `plt.show()`
- it should be run manually

### 5. Train The Machine Learning Model

Command:

```bash
python mlmodel_training.py
```

Input:
- `DataCSV/dataset_vehicles_enriched_MASTER.csv`

Output:
- `traffic_aimodel.pkl`

Model details:
- algorithm: `RandomForestClassifier`
- features: `speed_kmh`, `throttle`, `brake`, `steer`
- target: `incident_detected`

What to expect:
- console print: accuracy and classification report
- feature-importance chart
- confusion matrix

Note:
- this script also opens Matplotlib windows with `plt.show()`

### 6. Run Real-Time Risk Analysis

Command:

```bash
python vehicle_behavior_analysis.py
```

Inputs:
- `traffic_aimodel.pkl`
- `baronissi_base_map.xodr`

Outputs:
- live console alerts during execution
- `realtime_inference_results.txt`

What it does:
- loads the trained AI model
- recreates the Baronissi world from the OpenDRIVE file
- spawns and monitors traffic in CARLA
- runs inference vehicle by vehicle
- draws a red debug arrow over vehicles classified as risky
- logs total alerts, validated incidents, false positives, lead time, and inference latency

## Generated Artifacts

After a full Baronissi run, the main generated files are:
- `baronissi_base_map.xodr`
- `DataCSV/dataset_collisions_*.csv`
- `DataCSV/dataset_vehicles_enriched_MASTER.csv`
- `traffic_aimodel.pkl`
- `realtime_inference_results.txt`

## Important Notes

- Run scripts from the repository root. Several paths are hard-coded as relative paths such as `.\\DataCSV\\...` and `traffic_aimodel.pkl`.
- Several files execute their logic immediately on import, including `main_map_conversion.py`, `world_data_analysis.py`, `mlmodel_training.py`, and `vehicle_behavior_analysis.py`. Treat them as standalone scripts.
- CARLA connection settings are hard-coded in the scripts: host `localhost`, port `2000`, Traffic Manager port `8000`.


## Execution Path

If the goal is only to validate the full thesis workflow quickly:
1. start CARLA locally
2. run `python main_map_conversion.py` to generate Baronissi .xodr file (already present in repo)
3. ensure an active CARLA world already contains vehicles - if needed, execute `python init_torino_sim.py` to load Turin's base map as example. 
4. run `python init_main_map_registration.py` to generate individual CSV files.
5. run `python world_data_analysis.py` to generate Master dataset (already present in repo).
6. run `python mlmodel_training.py` to get RF model (already present in repo).
7. run `python vehicle_behavior_analysis.py`
8. inspect `DataCSV/dataset_vehicles_enriched_MASTER.csv`, `traffic_aimodel.pkl`, and `realtime_inference_results.txt`

## Quick Verification Path
1. start CARLA locally
2. run `python vehicle_behavior_analysis.py`
3. see real-time inference alerts. 


