
import csv

# PASOS PARA LA IMPLEMENTACIÓN  :
# 1) SOLO ESCOGUER LOS DATOS QUE ME IMPORTAN  ..
# 2)  COGER EL CSV Y TRABJAR CON BUFFERTS PARA PODER  MANEJAR CORRECTAMENTE LA INSERCCIÓN
# 3)  APLICAR EL AGLROTIMO VISTO EN CLASE 
# 4)  PASAR ESO  GUARDARLO EN UN ARCHIVO JSON
# LET'S GO   :) 

#  funcion para solo  coguer la daa que nos importa en este caso el name , el autor y  la letra de la canción


"""
import csv
import os

ruta_csv_original = r'C:\Users\semin\Downloads\spotify_songs.csv'
ruta_csv_simplificado = r'C:\Users\semin\Downloads\archivo_simplificado.csv'

if not os.path.exists(ruta_csv_original):
    print(f"El archivo original no existe en la ruta especificada: {ruta_csv_original}")
else:
    with open(ruta_csv_original, 'r', encoding='utf-8') as archivo_entrada:
        csv_lector = csv.reader(archivo_entrada)
        encabezado = next(csv_lector)
        idx_track_name = encabezado.index('track_name')
        idx_track_artist = encabezado.index('track_artist')
        idx_lyrics = encabezado.index('lyrics')

        with open(ruta_csv_simplificado, 'w', newline='', encoding='utf-8') as archivo_salida:
            csv_escritor = csv.writer(archivo_salida)
            csv_escritor.writerow(['track_name', 'track_artist', 'lyrics'])

            for fila in csv_lector:
                track_name = fila[idx_track_name]
                track_artist = fila[idx_track_artist]
                lyrics = fila[idx_lyrics]
                csv_escritor.writerow([track_name, track_artist, lyrics])

    print(f"Archivo simplificado creado en: {ruta_csv_simplificado}")



"""

import pandas as pd
import nltk

def tokenizar(texto):
    palabras = []
    palabra = ''
    for caracter in texto:
        if caracter.isalnum() or caracter == '-':
            palabra += caracter
        else:
            if palabra:
                palabras.append(palabra)
                palabra = ''
    if palabra:
        palabras.append(palabra)
    return palabras

def cargar_stopwords_nltk(idioma='english'):
    try:
        from nltk.corpus import stopwords
        return set(stopwords.words(idioma))
    except OSError:
        return set()

def eliminar_stopwords(lista_palabras, idioma='english'):
    stop_words = cargar_stopwords_nltk(idioma)
    return [palabra for palabra in lista_palabras if palabra.lower() not in stop_words]

def eliminar_puntuacion(lista_palabras):
    return [''.join(caracter for caracter in palabra if caracter.isalnum()) for palabra in lista_palabras if ''.join(caracter for caracter in palabra if caracter.isalnum())]

def reducir_palabras(lista_palabras):
    sufijos = ['ing', 'ed', 'ly', 'es', 's', 'ment', 'er', 'tion', 'able', 'ness', 'ful']
    palabras_reducidas = []
    for palabra in lista_palabras:
        for sufijo in sufijos:
            if palabra.endswith(sufijo):
                palabra = palabra[:-len(sufijo)]
                break
        palabras_reducidas.append(palabra)
    return palabras_reducidas

def Procesing(documento):
    tokens = tokenizar(documento)
    tokens = eliminar_stopwords(tokens)
    tokens = eliminar_puntuacion(tokens)
    tokens_reducidos = reducir_palabras(tokens)
    return tokens_reducidos

def ReadCVS(ruta_csv, sizeBuffer):
    with open(ruta_csv, 'r', encoding='utf-8') as archivo:
        encabezado = archivo.readline()  # Leer y descartar el encabezado
        buffer = []
        buffer_id = 1
        for linea in archivo:
            buffer.append(linea.strip())
            if len(buffer) == sizeBuffer:
                for documento in buffer:
                    buffer_procesing = Procesing(documento)
                    print(f"Buffer {buffer_id}, Documento Procesado: {buffer_procesing}")
                buffer = []
                buffer_id += 1
        if buffer:
            for documento in buffer:
                buffer_procesing = Procesing(documento)
                print(f"Buffer {buffer_id}, Documento Procesado: {buffer_procesing}")















import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

""""

documents = [
    (1, "el gato estÃ¡ en el tejado"),
    (2, "el perro estÃ¡ en el patio"),
    (3, "el gato duerme en el patio"),
    (4, "el pÃ¡jaro estÃ¡ en el tejado")
]

"""
"""
print("Tenemos : ")
print(len(documents))
print(".......")
"""
"""
def tokenizar(texto):
    palabras = []
    palabra = ''
    for caracter in texto:
        if caracter.isalnum() or caracter == '-':
            palabra += caracter
        else:
            if palabra:
                palabras.append(palabra)
                palabra = ''
    if palabra:
        palabras.append(palabra)
    return palabras

def cargar_stopwords_nltk(idioma='english'):
    try:
        return set(stopwords.words(idioma))
    except OSError:
        return set()

def eliminar_stopwords(lista_palabras, idioma='english'):
    stop_words = cargar_stopwords_nltk(idioma)
    return [palabra for palabra in lista_palabras if palabra.lower() not in stop_words]

def eliminar_puntuacion(lista_palabras):
    return [''.join(caracter for caracter in palabra if caracter.isalnum()) for palabra in lista_palabras if ''.join(caracter for caracter in palabra if caracter.isalnum())]

def reducir_palabras(lista_palabras):
    sufijos = ['ing', 'ed', 'ly', 'es', 's', 'ment', 'er', 'tion', 'able', 'ness', 'ful']
    palabras_reducidas = []
    for palabra in lista_palabras:
        for sufijo in sufijos:
            if palabra.endswith(sufijo):
                palabra = palabra[:-len(sufijo)]
                break
        palabras_reducidas.append(palabra)
    return palabras_reducidas

def procesar_documento(documento, idioma='english'):
    tokens = tokenizar(documento)
    tokens_filtrados = eliminar_stopwords(tokens, idioma)
    tokens_limpios = eliminar_puntuacion(tokens_filtrados)
    tokens_reducidos = reducir_palabras(tokens_limpios)
    indice_invertido = {}
    for idx, palabra in enumerate(tokens_reducidos):
        if palabra not in indice_invertido:
            indice_invertido[palabra] = []
        indice_invertido[palabra].append(idx)
   # print("Tokens:", tokens)
    #print("Tokens sin stopwords:", tokens_filtrados)
    #print("Tokens sin signos de puntuaciÃ³n:", tokens_limpios)
    #print("Tokens reducidos:", tokens_reducidos)
    print("\nÃndice invertido:", indice_invertido)

documento = "Hello, this is an example document. It contains punctuation, stopwords, and more!,Hello"
procesar_documento(documento, idioma='english')

documento2 = "Este es otro ejemplo para probar si las funciones funcionan para diferentes tipos de documentos, que contienen varios elementos."
procesar_documento(documento2, idioma='spanish')

"""

"""
    (1, "el gato estÃ¡ en el tejado"),
    (2, "el perro estÃ¡ en el patio"),
    (3, "el gato duerme en el patio"),
    (4, "el pÃ¡jaro estÃ¡ en el tejado")
DADO POR EJEMPLO ESTO : 
     1) token_stream = [("el", 1), ("gato", 1), ("estÃ¡", 1), ("en", 1), ("tejado", 1)]


"""
def buscar_valor(diccionario, clave):
    if clave in diccionario:
        return diccionario[clave]
    return None  # Devuelve None si la clave no se encuentra



"""
   # Verificar si la lista de postings estÃ¡ llena
        if len(lista_posting) >= 1000:
            # Doblar el tamaÃ±o de la lista de postings si es necesario (esto es ilustrativo)
            lista_posting.extend([None] * len(lista_posting))

        # AÃ±adir el docID a la lista de postings, evitando duplicados

"""
def SPIMI(PARSEO): 
    diccionario = {}  # diccionario en donde vamos a colocar los indices invertidos

    while PARSEO: 
        token = PARSEO.pop(0)  # el primer elemento de parseo 
        termino = token[0]
        ID = token[1]
        lista_posting = buscar_valor(diccionario, termino)

        if lista_posting is None:  # si no se encuentra el termino entonces creo una lista que tenga como key el termino
            lista_posting = []
            diccionario[termino] = lista_posting

        # AÃ±adir el  ID  
        if ID not in lista_posting:
            lista_posting.append(ID)

    return diccionario



def MergeBlocksSimple(blocks):
    merged_index = {}

    for block in blocks:
        for term, postings in block.items():
            if term not in merged_index:
                merged_index[term] = postings
            else:
                for posting in postings:
                    if posting not in merged_index[term]:
                        merged_index[term].append(posting)

    for term in merged_index:
        merged_index[term].sort()

    return merged_index



def ParserDocs(Doc): 
    lista_TOKENR=[]
    # todo procesamos 2 bloques 
    for i in range (3) :
        if len(Doc) == 0:
            break
        ID ,contenido=Doc.pop(0)
        #print("----------------")
        #print(ID,contenido)
        #print("--------------")
        tokens = contenido.split()  # Simulamos tokenizaciÃ³n dividiendo por espacios
        for elemento in tokens:
              lista_TOKENR.append((elemento,ID))


    return  lista_TOKENR

""""

XD TA AL REVES ESA COSA JSJSJSJS  
PARSEO :
[(1, 'el'), (1, 'gato'), (1, 'estÃ¡'), (1, 'en'), (1, 'el'), (1, 'tejado'), (2, 'el'), (2, 'perro'), (2, 'estÃ¡'), (2, 'en'), (2, 'el'), (2, 'patio')]
"""


def BSBIndexConstruction(Documento):
    n=0
    lista_todo=[]
    while Documento : 
         n+=1
         tokeniar=ParserDocs(Documento)  # todo hacer el parceo
         index_invertido= SPIMI(tokeniar)
         lista_todo.append(index_invertido)
    # combinar :)
    Final_merge=MergeBlocksSimple(lista_todo)
    return Final_merge
   
        
documents = [
    (1, "el gato estÃ¡ en el tejado"),
    (2, "el perro estÃ¡ en el patio"),
    (3, "el gato duerme en el patio"),
    (4, "el pÃ¡jaro estÃ¡ en el tejado")
]

print(BSBIndexConstruction(documents))


#print("PARSEO : ")
#value_input=ParserDocs(documents)
#print(value_input)
#print(".............SPIMI .............")
#print(SPIMI(value_input))
