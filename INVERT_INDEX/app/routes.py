from flask import Blueprint, render_template, request, jsonify
from .Final2 import IndiceInvertido, MotorConsulta

import json

main = Blueprint('main', __name__)


RUTA_INDICE_LOCAL = r"C:\Users\semin\BD2" 
RUTA_ARCHIVO_CSV = r"C:\Users\semin\BD2\spotify_songs.csv"  
RUTA_STOPLIST = r"C:\Users\semin\BD2\stoplist.csv"  
RUTA_NORMAS = r"C:\Users\semin\BD2\normas.json" 
RUTA_PESOS_CAMPO = r"C:\Users\semin\BD2\pesos_campos.json" 



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
    top_k = data.get('top_k', 10)
    print("Estoy en la Consutla")
    # Paso 4: Procesar la Consulta
    terminos_procesados = motor_busqueda.procesar_consulta(consulta_usuario)
    print("Términos Procesados de la Consulta:", terminos_procesados)

    # Paso 5: Buscar y Recuperar los Top K Resultados
    resultados_busqueda = motor_busqueda.buscar(consulta_usuario, top_k=top_k)
    print(f"Top {top_k} Resultados de Búsqueda:")
    print(json.dumps(resultados_busqueda, indent=2, ensure_ascii=False))
    
    return jsonify(resultados_busqueda)