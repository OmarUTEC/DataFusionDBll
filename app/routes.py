from flask import Blueprint, render_template, jsonify, request
from INVERT_INDEX.Final2 import generar_resultados_busqueda  # Asegúrate de importar la función correcta
import json
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')


    
"""
@main.route('/get_data', methods=['GET'])
def get_data():
    try:
        # Usamos una consulta fija
        consulta_usuario = "I Feel Alive"  # Consulta predefinida
        
        # Llamar a la función para generar los resultados de búsqueda
        generar_resultados_busqueda(consulta_usuario)  # Pasamos la consulta fija

        # Ruta del archivo donde se guardan los resultados
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_resultados = os.path.join(current_dir, 'app', 'resultados_busqueda.json')

        # Leer los datos del archivo JSON generado por la función
        with open(ruta_resultados, 'r', encoding='utf-8') as archivo:
            resultados = json.load(archivo)
        
        return jsonify(resultados)

    except FileNotFoundError:
        return jsonify({"error": "Archivo no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

@main.route('/get_data', methods=['GET'])
def get_data():
    try:
        # Ruta del archivo donde se guardan los resultados (en el mismo directorio que este archivo)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_resultados = os.path.join(current_dir, 'resultados_busqueda.json')  # Ajusta la ruta

        # Leer los datos del archivo JSON generado por la función
        with open(ruta_resultados, 'r', encoding='utf-8') as archivo:
            resultados = json.load(archivo)
        
        return jsonify(resultados)

    except FileNotFoundError:
        return jsonify({"error": "Archivo no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para mostrar los resultados
@main.route('/results')
def show_results():
    return render_template('get_data.html')
