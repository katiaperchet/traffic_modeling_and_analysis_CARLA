import carla

def main():
    # Conectar al simulador
    client = carla.Client('localhost', 2000)
    client.set_timeout(15.0)

    # Ruta a tu archivo (usa r'' para rutas de Windows)
    path = r"C:\Users\katia\Documents\UNISA\THESIS\traffic_modelling_and_analysis_CARLA\torino.xodr"

    try:
        with open(path, 'r', encoding='utf-8') as f:
            xodr_content = f.read()
        
        # Parámetros para que el mapa no sea invisible
        params = carla.OpendriveGenerationParameters(
            vertex_distance=2.0,
            max_road_length=50.0,
            wall_height=0.0,
            additional_width=0.6,
            smooth_junctions=True,
            enable_mesh_visibility=True  # ESTO CREA LA MALLA VISUAL
        )

        print("Cargando Torino en CARLA... Esto puede tardar unos segundos.")
        client.generate_opendrive_world(xodr_content, params)
        print("¡Mapa cargado con éxito!")

    except Exception as e:
        print(f"Error al cargar el mapa: {e}")

if __name__ == '__main__':
    main()