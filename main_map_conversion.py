import io
import carla

f = io.open("baronissi_base.osm", mode="r", encoding="utf-8")
osm_data = f.read()
f.close()

settings = carla.Osm2OdrSettings()
settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

f = open("baronissi_base_map.xodr", 'w')
f.write(xodr_data)
f.close()