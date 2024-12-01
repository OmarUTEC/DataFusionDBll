# Proyecto: Búsqueda y Recuperación de la Información

### Descripción
Este proyecto es una aplicación web que permite realizar búsquedas avanzadas en una base de datos de canciones de Spotify, mostrando información relevante como ID, nombre, artista, popularidad y álbum. Combina un backend en Python con Flask y PostgreSQL con un frontend desarrollado en HTML, CSS y JavaScript.

---

## Características principales
- Búsqueda optimizada utilizando índice invertido
- Visualización de resultados con campos clave:
  - `Track ID`
  - `Track Name`
  - `Track Artist`
  - `Track Popularity`
  - `Track Album Name`
- Selección dinámica entre dos tablas con diferentes estructuras (`Indice invertido` y `Indice Postgresql`).
- Interfaz de usuario amigable con resultados interactivos.
- Medición y visualización del tiempo de consulta.

---

## Tecnologías utilizadas
### Backend
- **Python 3.10** 
- **Flask**: Framework para construir el servidor y manejar las rutas.
- **PostgreSQL**: Base de datos relacional para almacenar información musical.
- **psycopg2**: Librería para conectar Python con PostgreSQL.

### Frontend
- **HTML/CSS/JavaScript**: Construcción de la interfaz.
- **Fetch API**: Manejo de solicitudes HTTP para conectar el frontend con el backend.

---

## Estructura del Proyecto
```plaintext
📁 Proyecto
│
├── 📂 backend
│   ├── app.py                 # Archivo principal de Flask
│   ├── consulta_db.py         # Lógica de consultas a PostgreSQL
│   └── requirements.txt       # Dependencias del proyecto
│
├── 📂 frontend
│   ├── index.html             # Interfaz de usuario
│   ├── styles.css             # Estilos personalizados
│   └── script.js              # Lógica de interacción con el usuario
│
└── README.md                  # Documentación del proyecto
```

# Organización del equipo

| Participante      | Papel |
|-------------------|-------|
| Aldair Seminario | Creación de índice invertido, Implementación de SPIMI para busqueda textual y diseño de frontend|
| Nicol Campoverde | Adaptación del frontend con el backend y implementación de busqueda por imágenes                |
| OMAR             | Procesamiento de archivos csv y además  del desarrollo de la base de datos en postgres          |



# Introducción
- [Objetivo del proyecto](#Datos)
- [Librerías utilizadas](#librerías-utilizadas)
- [Técnicas de indexación (usando indice invertido)](#técnica-de-indexación-de-las-librerías-utilizadas---índice-multimedia)
- [Ténica Multimedia (usando Knn)](#como-se-realiza-el-knn-search-y-el-range-search)

## Backend
- [Construcción del índice invertido](#construcción-del-índice-invertido)
- [Construcción del indice Multimedia](#manejo-de-memoria-secundaria)
- [Manejo de memoria secundaria](#ejecución-óptima-de-consultas)

## Análisis de Tamaño de Buffert
- [Análisis sobre los Bufferts ](#análisis-de-la-maldición-de-la-dimensionalidad-y-cómo-mitigarlo)

## Frontend
- [Diseño del índice con PostgreSQL](#diseño-del-índice-con-postgresql)
- [Análisis comparativo con su propia implementación](#análisis-comparativo-con-su-propia-implementación)
- [Screenshots de la GUI](#screenshots-de-la-gui)

## Experimentación
- [Resultados de la query](#resultados-de-la-query)
- [Análisis y discusión](#análisis-y-discusión)

<!-- Secciones -->

## 1)Objetivo del proyecto
Este proyecto tiene como objetivo diseñar e implementar un sistema de búsqueda y recuperación de datos, ya sean datos multimedia o textuales. Se utilizan estructuras de datos vistas en el curso de Bases de Datos 2, tales como:

- Índice invertido
- Similitud del coseno
- Búsqueda por rango

Además, se busca que la experiencia del usuario en la interfaz gráfica sea lo más amigable y 
entendible posible para facilitar el manejo de nuestro producto.


## 1) Datos

### 1.1) Búsquedas textuales:
El dataset Spotify Songs es un archivo CSV que contiene información sobre diversas canciones.
Este archivo incluye detalles como el álbum al que pertenece cada canción, la letra, y 
otros atributos relevantes que se utilizarán para trabajar en el proyecto. Es importante tener en 
cuenta que el archivo contiene un total de 18,456 registros.

<img src="./screenshot/multimedia_C.png" width="800"/>

### 1.2) Búsquedas por imágenes:

En cuanto a las búsquedas por imágenes, debido a la falta de un dataset completo que 
contenga tanto imágenes como descripciones, decidimos trabajar con un dataset separado.
Este dataset contiene 44,000 fotos de productos comunes que se encuentran en una tienda.
Estas imágenes serán utilizadas en el proyecto para realizar las búsquedas visuales.

![imágen del csv ](./screenshot/multimedia_C.png){: width="100px" }




## Librerías utilizadas
### Para el indice invertido 
```python
import os
import io
import json
import math
import pandas as pd
import nltk
from nltk.stem import SnowballStemmer
from collections import defaultdict
from typing import Dict
```

### Para el indice Multidimencional :

```python
import struct
import numpy as np
import heapq
import pandas as pd
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.applications.inception_v3 import preprocess_input
import json
import os
import requests
from io import BytesIO
import gc
from tempfile import NamedTemporaryFile
```

#### 1. `json`
- **Propósito**: Permite leer y escribir datos en formato JSON
- **Uso**: Se utiliza para cargar datos desde archivos JSON y guardar resultados procesados en dicho formato.
  
  ```python
  with open(ruta_indice_parcial, 'w', encoding='utf-8') as archivo:
    json.dump(self.indice_invertido, archivo)

  # para cargar un json 
  with open(self.ruta_pesos, 'r', encoding='utf-8') as archivo:
    self.pesos_campos = json.load(archivo)
  ```
#### 2. `nltk`
- **Propósito**: Proporciona  librerias para el procesamiento y análisis de texto en lenguaje natural.
- **Uso**: Lo utilizamos para tareas como la tokenización, stemming, y análisis de texto.
```python
import nltk
from nltk.stem import SnowballStemmer
nltk.download('punkt')  # Descargar recursos de tokenización
stemmer = SnowballStemmer('spanish')
```

#### 3. `os`
- **Propósito**: permite  manejar rutas de archivos y directorios.
- **Uso**: Se utiliza para gestionar rutas de acceso a archivos json , crear directorios, verificar la existencia de los mismos.
```python
ruta_completa = os.path.join(self.ruta_indice, "archivo.json")

```


#### 3. `NumPy `
- **Propósito**: biblioteca fundamental para el cálculo numérico en Python,nos permite realizar operaciones matemáticas
- **Uso**:  Se utiliza para varias operaciones matemáticas como  :  la distancia euclidiana entre vectores y operaciones entre arrays.
```python
def euclidean_distance(self, x, y):
    return np.sqrt(np.sum((x - y) ** 2))

with open(self.binary_file, 'rb') as f:
    f.seek(position)
    data = f.read(4 + 4 * self.vector_size)
    if len(data) < 4 + 4 * self.vector_size:
        return None
    vector = np.array(struct.unpack(f'{self.vector_size}f', data[4:]))
```
#### 4. `Pandas`
- **Propósito**: Pandas es una biblioteca clave en Python que nos ayudara a trabajar con datos de manera sencilla, en este caso ns ayudara a manejar el csv .
- **Uso**: Se utilizo pandas  para cargar y leer los archivos csv.
```python
#  Cargar los datos
self.url_map = pd.read_csv(url_csv_file)
```
#### 5. ` TensorFlow Keras`
- **Propósito**:  TensorFlow Keras es una biblioteca poderosa que facilita la creación y entrenamiento de modelos de aprendizaje profundo. En este caso,
se utiliza para trabajar con un modelo preentrenado, específicamente InceptionV3, que ayuda a extraer características de imágenes.
- **Uso**:  Se utiliza para cargar un modelo preentrenado y procesar imágenes.
```python
#  Cargar el modelo
modelo_inception = InceptionV3(weights='imagenet', include_top=False, pooling='avg')
# Procesar Imágenes
img_array = preprocess_input(img_array)
vector = modelo_inception.predict(img_array).flatten()
```

[Contenido de la sección aquí]

## Técnica de indexación de las librerías utilizadas - Índice  invertido

En la implementación del índice invertido, se ha optado por una estrategia que permite manejar eficientemente grandes volúmenes de datos, 
asegurando un uso óptimo de la memoria y un acceso rápido a los registros.
A continuación se describen los principales aspectos de esta técnica:

### Carga de Datos en Chunks

- El procesamiento de datos se realiza en **chunks** (porciones) de tamaño definido (`TAMANIO_CHUNK`), lo que permite cargar solo una parte del dataset en memoria principal.
-  Esto evita la sobrecarga de memoria y mejora el rendimiento al trabajar con datasets extensos.

### Construcción del Índice Invertido
- Se crea un índice invertido que asocia cada término con los IDs de los documentos donde aparece.
  Esta estructura facilita las búsquedas rápidas, ya que permite acceder directamente a los documentos relevantes sin necesidad de escanear todo el conjunto de datos.

### Almacenamiento de IDs y Características

- Los IDs de los documentos se almacenan en un archivo de forma que se pueden recuperar fácilmente. Además, las características de los documentos se calculan y almacenan en un formato que permite un acceso eficiente.
 Esto se complementa con el uso de técnicas de **normalización logarítmica** para calcular la frecuencia de los términos, lo que mejora la precisión de las consultas.

### Manejo de Stopwords

- Se implementa un mecanismo para filtrar palabras irrelevantes (stopwords) utilizando una lista cargada desde un archivo externo. Esto ayuda a reducir el ruido en las consultas y a mejorar la relevancia de los resultados.

### Búsqueda y Recuperación

- El motor de consulta utiliza el índice invertido para procesar las consultas de manera eficiente. Se calcula la similitud coseno entre los términos de la consulta y los documentos en el índice, permitiendo una recuperación rápida de los documentos más relevantes.

## Beneficios

- **Eficiencia en la Búsqueda**: La estructura del índice invertido permite realizar búsquedas rápidas y efectivas, reduciendo el tiempo de respuesta al evitar búsquedas lineales en grandes conjuntos de datos.
- **Optimización del Uso de Recursos**: Al cargar datos en chunks y almacenar características en memoria secundaria, se maximiza el uso de la memoria, lo que es crucial para el manejo de grandes volúmenes de información.



## Técnica de indexación  Indice Multidimencional



## Como se realiza el KNN Search y el Range Search
[Contenido de la sección aquí]

## Construcción del índice invertido
[Contenido de la sección aquí]

## Manejo de memoria secundaria
[Contenido de la sección aquí]

## Ejecución óptima de consultas
[Contenido de la sección aquí]

## Análisis de la maldición de la dimensionalidad y cómo mitigarlo
[Contenido de la sección aquí]

## Diseño del índice con PostgreSQL
[Contenido de la sección aquí]

## Análisis comparativo con su propia implementación
[Contenido de la sección aquí]

## Screenshots de la GUI
[Contenido de la sección aquí]

## Resultados de la query
[Contenido de la sección aquí]

## Análisis y discusión
[Contenido de la sección aquí]










## Interfaz del usuario principal

![Interfaz de usuario](./screenshot/main.jpeg)

## Resultados de búsqueda index invertido 

![Resultados de búsqueda](./screenshot/interfaz_1.png)

## Interfaz del usuario principal para Busqueda de imágenes
![Resultados de búsqueda](./screenshot/interfaz_2.png)


## Resultados de búsqueda  de imágenes 

![Resultados de búsqueda](./screenshot/R1.png)

## IMPLEMENTACIÓN DEL INDICE INVERTIDO PARA LA BUSQUEDA TEXTUAL 
Clase
## Resultados de búsqueda index postgresql

![Resultados de búsqueda](./screenshot/postgresql.jpeg)
