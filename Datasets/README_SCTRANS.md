## SCTrans Dataset: Fix and modification logs
This document details the filtering, technical modifications, and access protocols applied to the SCTrans Dataset used in this research to ensure compatibility with the CARLA simulator (v0.9.16) and the integrity of the training telemetry.

## Dataset access
The SCTrans dataset is a private collection, to replicate the results of this study or to use the raw files, you must request access via the official repository:

- Official Link: https://github.com/SCTrans-Dataset/SCTrans

## Fix pipeline
The original dataset contains 1,417 unique traffic scenarios. To prioritize data quality and geographical consistency for this research, the following filters were applied:

- Geographic Filtering: Scenarios were restricted to Italian road topologies to align with the target area. This reduced the initial pool to 40 scenarios.

- Integrity Audit: Raw files were tested for topology consistency. Fragmented road networks that caused physics "voids" or agent spawning errors were discarded.

- Final Selection: 17 high-fidelity scenarios were successfully validated and executed using the ScenarioRunner package.

## Technical modifications
Some specific code modifications and XML repairs are required to execute the SCTrans scenarios within the required [ScenarioRunner environment - CARLA 0.9.13](https://github.com/seclab-fudan/SCTrans/tree/main/scenario-runner).

### ScenarioRunner patches
To resolve integration errors between OpenDrive-based maps and the ScenarioRunner framework, the following Python files were modified:

- openscenario_configuration.py (_set_carla_town method): Modified the logic for retrieving .xodr paths. This patch allows the system to recognize local map files when both .xosc and .xodr are located in the root directory of the patched ScenarioRunner, bypassing default package path restrictions.

- atomic_behaviors.py (Line 1973): Added a safety check during the Autopilot assignment. If a vehicle model is not suitable for the autopilot controller, the system now skips the assignment instead of triggering a fatal exception, preventing the simulation from breaking mid-run.

### OpenSCENARIO (.xosc) fixes
Every scenario from the SCTrans dataset underwent a manual fix process to ensure physical and logical stability:

#### Version downgrade (v1.1 to v1.0)

- Problem: The <SpeedProfileAction> tag (point-by-point speed profiling) is only supported in modern OpenSCENARIO versions not compatible with CARLA 0.9.13.

- Solution: Replaced with <SpeedAction> using a fixed AbsoluteTargetSpeed.

- Result: Resolved XMLSchemaChildrenValidationError and allowed scenarios to load successfully.

#### Z-Axis adjustment
- Problem: In pure OpenDrive maps, vehicles spawned exactly at z="0.0", causing them to be embedded in the road or stuck in "voids," leading to NoneType errors as CARLA deleted the actors.

- Solution: Manually updated all TeleportAction and WorldPosition coordinates from z="0.0" to z="0.2".

- Result: Allows the vehicle to drop onto the collision mesh, preventing physics collapse at simulation start.

#### Ego-vehicle order
- Problem: Issuing a RoutingAction before the vehicle was physically placed on the map caused silent crashes.

- Solution: Reordered the XML blocks to ensure <TeleportAction> is the first action performed.

- Result: Guarantees the actor exists physically before the controller attempts to calculate navigation routes.

#### Simulation time control
- Problem: ScenarioRunner would terminate the simulation as soon as the first success condition was met (often instantly).

- Solution: Added a KeepAliveEvent with a 1000-second timer. Also, modified the <StopTrigger> to a SimulationTimeCondition of 1000.0s.

- Result: Maintained the simulation long enough to collect the high-frequency telemetry required for the Master Dataset.

#### Asset consistency
- Problem: The default vehicle.lincoln.mkz2017 model was often missing or caused spawning errors in the "WindowsNoEditor" build.

- Solution: Globally replaced entity models with vehicle.tesla.model3.

- Result: Eliminated "Actor model not available" errors and ensured consistent sensor placement across all scenarios.

### Validated locations
The following Italian urban layouts were successfully stabilized and included in the final Master Dataset: 

Adelfia, Carpi, Empoli, Foggia, San Giorgio a Cremano, Segrate, and Siderno.

### Physics stability measures
Due to inherent conversion artifacts between OSM/XODR formats, all modified scenarios were executed with the Z-axis recovery algorithm and sub-asphalt collision platforms described on the thesis. These measures prevent telemetry corruption caused by vehicle glitches during complex maneuvers.