import io
import carla

# Read the .osm data
f = io.open("baronissi_base.osm", mode="r", encoding="utf-8")
osm_data = f.read()
f.close()

settings = carla.Osm2OdrSettings()
# Set OSM road types to export to OpenDRIVE
settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
# Convert to .xodr
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
f = open("baronissi_base_map.xodr", 'w')
f.write(xodr_data)
f.close()