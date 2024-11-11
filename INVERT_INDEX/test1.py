import os
import io
import json
import math
import pandas as pd
import nltk
from nltk.stem import SnowballStemmer
from collections import defaultdict
from typing import Dict

# Descargar datos necesarios de nltk
nltk.download('punkt')

# Definición de constantes
TAMANIO_CHUNK = int(io.DEFAULT_BUFFER_SIZE * 4.15)  # Número de filas por chunk
RUTA_INDICE_LOCAL = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX"
RUTA_INDICE_FINAL = r"/home/omarch/Escritorio/BD2/DataFusionDBll/INVERT_INDEX"
RUTA_ARCHIVO_CSV = r"../test.csv"
RUTA_STOPLIST = r"stopwords_personalizadas.csv"
RUTA_NORMAS = r"normas.json"
RUTA_PESOS_CAMPO = r"pesos_campos.json"  # Ruta para los pesos preprocesados


class IndiceInvertido:
    def __init__(self, ruta_csv: str, ruta_stoplist: str, ruta_indice: str, ruta_normas: str, ruta_pesos: str):
        # Inicialización de parámetros
        self.ruta_csv = ruta_csv
        self.ruta_stoplist = ruta_stoplist
        self.ruta_indice = ruta_indice
        self.ruta_normas = ruta_normas
        self.ruta_pesos = ruta_pesos
        self.stopwords = set()
        self.stemmer = SnowballStemmer('spanish')
        self.pesos_campos = []
        self.indice_invertido = defaultdict(dict)
        self.normas_documentos = {}
        
        # Cargar datos
        self._cargar_stopwords()
        self._cargar_pesos_campos()  # Cargar los pesos desde el archivo

    def _cargar_stopwords(self):
        """Cargar stopwords desde el archivo stoplist y añadir caracteres extendidos."""
        try:
            with open(self.ruta_stoplist, 'r', encoding='utf-8') as archivo:
                for linea in archivo:
                    palabra = linea.strip().lower()
                    if palabra:
                        self.stopwords.add(palabra)
            print("Stopwords cargadas (IndiceInvertido):", self.stopwords)
        except FileNotFoundError:
            print(f"Archivo de stopwords no encontrado en {self.ruta_stoplist}")
        
        # Añadir caracteres especiales
        caracteres_especiales = set("'«[]¿?$+-*'.,»:;!,º«»()@¡“/#|*%'&`")
        self.stopwords.update(caracteres_especiales)

    def _cargar_pesos_campos(self):
        """Carga los pesos de los campos desde un archivo JSON."""
        try:
            with open(self.ruta_pesos, 'r', encoding='utf-8') as archivo:
                self.pesos_campos = json.load(archivo)
            print(f"Pesos de campos cargados desde {self.ruta_pesos}: {self.pesos_campos}")
        except FileNotFoundError:
            print(f"Archivo de pesos no encontrado en {self.ruta_pesos}")
            self.pesos_campos = []

    def construir_indice(self):
        """Construir el índice invertido a partir del archivo CSV."""
        numero_chunk = 0
        try:
            for chunk in pd.read_csv(self.ruta_csv, chunksize=TAMANIO_CHUNK, encoding='utf-8'):
                numero_chunk += 1
                print(f"Procesando chunk {numero_chunk}")
                self._procesar_chunk(chunk)
                self._guardar_indice_parcial(numero_chunk)
            self._guardar_normas()
            print("Construcción del índice invertido completada.")
        except Exception as e:
            print(f"Error al construir el índice: {e}")

    def _procesar_chunk(self, chunk: pd.DataFrame):
        """Procesar un chunk del archivo CSV y actualizar el índice invertido y las normas."""
        for indice, fila in chunk.iterrows():
            id_documento = str(indice)  # Convertir id_documento a cadena para consistencia
            self.normas_documentos[id_documento] = 0
            frecuencia_terminos = defaultdict(float)
            
            for idx_campo, campo in enumerate(fila):
                if idx_campo >= len(self.pesos_campos):
                    continue  # Saltar campos sin pesos definidos
                peso = self.pesos_campos[idx_campo]
                if peso == 0:
                    continue  # Saltar campos con peso cero
                tokens = nltk.word_tokenize(str(campo).lower())
                tokens = [token.strip() for token in tokens]
                for token in tokens:
                    if token not in self.stopwords:
                        lematizado = self.stemmer.stem(token)
                        frecuencia_terminos[lematizado] += peso
                    else:
                        pass  # Stopwords eliminadas
                
            # Actualizar índice invertido y normas
            for termino, frecuencia in frecuencia_terminos.items():
                self.indice_invertido[termino][id_documento] = math.log10(1 + frecuencia)
                self.normas_documentos[id_documento] += self.indice_invertido[termino][id_documento] ** 2

    def _guardar_indice_parcial(self, numero_chunk: int):
        """Guardar el estado actual del índice invertido en un archivo JSON."""
        ruta_indice_parcial = os.path.join(self.ruta_indice, f"indice_parcial_{numero_chunk}.json")
        try:
            with open(ruta_indice_parcial, 'w', encoding='utf-8') as archivo:
                json.dump(self.indice_invertido, archivo)
            print(f"Índice parcial guardado en {ruta_indice_parcial}")
            self.indice_invertido.clear()  # Limpiar índice en memoria después de guardar
        except Exception as e:
            print(f"Error al guardar el índice parcial: {e}")

    def _guardar_normas(self):
        """Guardar las normas de los documentos en un archivo JSON."""
        try:
            # Convertir id_documento a cadena para consistencia
            normas_str_keys = {str(k): round(math.sqrt(v), 3) for k, v in self.normas_documentos.items()}
            with open(self.ruta_normas, 'w', encoding='utf-8') as archivo:
                json.dump(normas_str_keys, archivo)
            print(f"Normas guardadas en {self.ruta_normas}")
        except Exception as e:
            print(f"Error al guardar las normas: {e}")


class MotorConsulta:
    def __init__(self, ruta_csv: str, ruta_indice: str, ruta_normas: str, ruta_stoplist: str):
        # Inicialización de parámetros
        self.ruta_csv = ruta_csv
        self.ruta_indice = ruta_indice
        self.ruta_normas = ruta_normas
        self.ruta_stoplist = ruta_stoplist
        self.stemmer = SnowballStemmer('spanish')
        self.stopwords = set()
        
        # Cargar datos
        self._cargar_stopwords()
        self.indice_invertido = self._cargar_indice_completo()
        self.normas_documentos = self._cargar_normas()
        
        # Cargar el DataFrame completo una vez para evitar cargarlo múltiples veces
        self.dataframe = pd.read_csv(self.ruta_csv, index_col=None, encoding='utf-8', low_memory=False)
        self.dataframe.reset_index(drop=True, inplace=True)
        self.dataframe.index = self.dataframe.index.map(str)  # Convertir índices a str para consistencia

    def _cargar_stopwords(self):
        """Cargar stopwords desde el archivo stoplist y añadir caracteres extendidos."""
        try:
            with open(self.ruta_stoplist, 'r', encoding='utf-8') as archivo:
                for linea in archivo:
                    palabra = linea.strip().lower()
                    if palabra:
                        self.stopwords.add(palabra)
            print("Stopwords cargadas (MotorConsulta):", self.stopwords)
        except FileNotFoundError:
            print(f"Archivo de stopwords no encontrado en {self.ruta_stoplist}")
        
        # Añadir caracteres especiales
        caracteres_especiales = set("'«[]¿?$+-*'.,»:;!,º«»()@¡“/#|*%'&`")
        self.stopwords.update(caracteres_especiales)

    def _cargar_indice_completo(self) -> Dict[str, Dict[str, float]]:
        """Cargar todos los archivos parciales del índice invertido y fusionarlos en un índice completo."""
        indice_completo = defaultdict(dict)
        try:
            for nombre_archivo in os.listdir(self.ruta_indice):
                if nombre_archivo.startswith("indice_parcial_") and nombre_archivo.endswith(".json"):
                    ruta_archivo = os.path.join(self.ruta_indice, nombre_archivo)
                    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                        indice_parcial = json.load(archivo)
                        for termino, postings in indice_parcial.items():
                            indice_completo[termino].update(postings)
            print("Índice invertido completo cargado.")
            return indice_completo
        except Exception as e:
            print(f"Error al cargar el índice invertido: {e}")
            return defaultdict(dict)

    def _cargar_normas(self) -> Dict[str, float]:
        """Cargar las normas de los documentos desde el archivo JSON."""
        try:
            with open(self.ruta_normas, 'r', encoding='utf-8') as archivo:
                normas = json.load(archivo)
            return normas
        except Exception as e:
            print(f"Error al cargar las normas: {e}")
            return {}

    def obtener_resultados_relevantes(self, consulta: str, cantidad_resultados: int = 10) -> pd.DataFrame:
        """Obtener los resultados relevantes de la consulta dada en función de la similitud coseno."""
        resultados = []
        consulta_lematizada = [self.stemmer.stem(token.lower()) for token in nltk.word_tokenize(consulta)]
        
        # Filtrar tokens de stopwords
        consulta_lematizada = [token for token in consulta_lematizada if token not in self.stopwords]

        # Calcular similitud coseno
        for id_documento, fila in self.dataframe.iterrows():
            suma_similitud = 0
            norma_documento = self.normas_documentos.get(str(id_documento), 0)
            if norma_documento == 0:
                continue  # Ignorar documentos sin norma
            
            for token in consulta_lematizada:
                if token in self.indice_invertido:
                    if str(id_documento) in self.indice_invertido[token]:
                        suma_similitud += self.indice_invertido[token][str(id_documento)]

            similitud_coseno = suma_similitud / norma_documento if norma_documento > 0 else 0
            resultados.append({'id_documento': str(id_documento), 'similitud': similitud_coseno, 'documento': fila})

        # Ordenar resultados por similitud coseno
        resultados_ordenados = sorted(resultados, key=lambda x: x['similitud'], reverse=True)[:cantidad_resultados]

        # Crear un DataFrame con los resultados
        df_resultados = pd.DataFrame([r['documento'] for r in resultados_ordenados])
        return df_resultados


# Caso de prueba para verificar la construcción del índice y la consulta

# Definir rutas de los archivos de entrada
ruta_csv = "../test.csv"
ruta_stoplist = "stopwords_personalizadas.csv"
ruta_indice = "INVERT_INDEX"  # Ruta donde se guardarán los archivos del índice invertido
ruta_normas = "normas.json"
ruta_pesos = "pesos_campos.json"

# Crear una instancia de la clase IndiceInvertido
indice = IndiceInvertido(ruta_csv, ruta_stoplist, ruta_indice, ruta_normas, ruta_pesos)

# Construir el índice invertido
indice.construir_indice()

# Crear una instancia de la clase MotorConsulta
motor_consulta = MotorConsulta(ruta_csv, ruta_indice, ruta_normas, ruta_stoplist)

# Realizar una consulta de ejemplo
consulta = "Python programación"
resultados = motor_consulta.obtener_resultados_relevantes(consulta, cantidad_resultados=3)

# Mostrar los resultados
print("Resultados de la consulta:")
print(resultados)
