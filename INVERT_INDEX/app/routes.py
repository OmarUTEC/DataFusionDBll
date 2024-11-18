from flask import Blueprint, render_template, request, jsonify
from .Final2 import IndiceInvertido, MotorConsulta

import psycopg2
import json
import time

main = Blueprint('main', __name__)

"""
RUTA_INDICE_LOCAL = r"C:/Users/semin/BD2" 
RUTA_ARCHIVO_CSV = r"C:/Users/semin/BD2/spotify_songs.csv"  
RUTA_STOPLIST = r"C:/Users/semin/BD2/stoplist.csv"  
RUTA_NORMAS = r"C:/Users/semin/BD2/normas.json" 
RUTA_PESOS_CAMPO = r"C:/Users/semin/BD2/pesos_campos.json" 
"""

TAMANIO_CHUNK = 467258 #  filas por chunk esto basandonos en el uso del 10%de la memoria disponible
RUTA_INDICE_LOCAL = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX"
RUTA_INDICE_FINAL = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX"
RUTA_ARCHIVO_CSV = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX/spotify_songs.csv"
RUTA_STOPLIST = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX/stoplist.csv"
RUTA_NORMAS = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX/normas.json"  # ruta normas 
RUTA_PESOS_CAMPO = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX/pesos_campos.json"


"""
   # Paso 2: Construir el indice Invertido
indice = IndiceInvertido(
        ruta_csv=RUTA_ARCHIVO_CSV,
        ruta_stoplist=RUTA_STOPLIST,
        ruta_indice=RUTA_INDICE_LOCAL,
        ruta_normas=RUTA_NORMAS,
        ruta_pesos=RUTA_PESOS_CAMPO  # ruta para los pesos preprocesados
    )
indice.construir_indice()# Inicializar el Motor de Consulta una vez al iniciar la aplicación
"""

motor_busqueda = MotorConsulta(
    ruta_csv=RUTA_ARCHIVO_CSV,
    ruta_indice=RUTA_INDICE_LOCAL,
    ruta_normas=RUTA_NORMAS,
    ruta_stoplist=RUTA_STOPLIST
)


@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/consulta', methods=['POST'])
def consulta():
    data = request.get_json()
    consulta_usuario = data.get('consulta', '')
    top_k = data.get('top_k', 10)  # Se recibe también el parámetro top_k
    
    print("Estoy en la consulta del índice invertido")

    # Paso 4: Procesar la Consulta para el Índice Invertido
    terminos_procesados = motor_busqueda.procesar_consulta(consulta_usuario)
    print("Términos Procesados de la Consulta:", terminos_procesados)

    # Paso 5: Buscar y Recuperar los Top K Resultados del Índice Invertido
    resultados_busqueda = motor_busqueda.buscar(consulta_usuario, top_k=top_k)
    print(f"Top {top_k} Resultados de Búsqueda en el Índice Invertido:")
    print(json.dumps(resultados_busqueda, indent=2, ensure_ascii=False))

    return jsonify(resultados_busqueda)

def search_in_db(search_query, top_k=10):
    try:
        conn = psycopg2.connect(
            dbname="spotify_songs",
            user="postgres",
            password="admin123",
            host="localhost", 
            port="5432"  
        )

        cursor = conn.cursor()

        cursor.execute("""
            SELECT track_id, track_name, track_artist, track_popularity, track_album_name
            FROM spotify_songs
            WHERE search_vector @@ plainto_tsquery('english', %s)
            LIMIT %s;
        """, (search_query, top_k))

        results = cursor.fetchall()
        result_json = {}

        # Procesar cada fila de los resultados y agregarla al diccionario con índices numéricos como claves
        if results:
            for index, row in enumerate(results):
                result_json[index + 1] = { 
                    "track_id": row[0],            # Track ID
                    "track_name": row[1],          # Track Name
                    "track_artist": row[2],        # Track Artist
                    "track_popularity": row[3],    # Track Popularity
                    "track_album_name": row[4]     # Track Album Name
                }
        else:
            result_json = {"1": "No se encontraron resultados."}

        cursor.close()
        conn.close()

        return result_json
    except Exception as e:
        return {"error": str(e)}

@main.route('/consulta_db', methods=['POST'])
def consulta_db():
    data = request.get_json()
    consulta_usuario = data.get('consulta', '')
    top_k = data.get('top_k', 10)  

    print("Estoy en la consulta de la base de datos PostgreSQL")
    song_data = search_in_db(consulta_usuario, top_k)
    print(json.dumps(song_data, indent=2, ensure_ascii=False)) 

    return jsonify(song_data)
