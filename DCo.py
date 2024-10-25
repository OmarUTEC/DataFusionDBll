import csv
import nltk
import json

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

def ReadCVS(ruta_csv, sizeBuffer, ruta_json):
    resultado = []  # Para almacenar los documentos procesados
    
    with open(ruta_csv, 'r', encoding='utf-8') as archivo:
        encabezado = archivo.readline()  # eer y descartar el encabezado
        buffer = []
        buffer_id = 1
        for linea in archivo:
            buffer.append(linea.strip())
            if len(buffer) == sizeBuffer:
                for documento in buffer[:5]:  # Mostrar solo los primeros 5 documentos procesados del buffer
                    buffer_procesing = Procesing(documento)
                    resultado.append({
                        'buffer_id': buffer_id,
                        'documento_procesado': buffer_procesing
                    })
                    print(f"Buffer {buffer_id}, Documento Procesado (muestra): {buffer_procesing}")
                buffer = []
                buffer_id += 1
        if buffer:
            for documento in buffer[:5]:  # Mostrar solo los primeros 5 documentos procesados del buffer restante
                buffer_procesing = Procesing(documento)
                resultado.append({
                    'buffer_id': buffer_id,
                    'documento_procesado': buffer_procesing
                })
                print(f"Buffer {buffer_id}, Documento Procesado (muestra): {buffer_procesing}")

    # Guardar los resultados en un archivo JSON
    with open(ruta_json, 'w', encoding='utf-8') as archivo_json:
        json.dump(resultado, archivo_json, indent=4, ensure_ascii=False)

# Llamar a la funciOn con la ruta y el tamaño del buffer deseado
ruta_csv = r'C:\Users\semin\OneDrive\Escritorio\bd2\archivo_simplificado.csv'
sizeBuffer = 100
ruta_json = r'C:\Users\semin\OneDrive\Escritorio\bd2\archivo_PROCESADO2.json'

ReadCVS(ruta_csv, sizeBuffer, ruta_json)
