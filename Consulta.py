
import json
import math
from collections import defaultdict

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

import json
import math
from collections import defaultdict

def cargar_indice(ruta_json):
    """Carga el índice invertido desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)

def procesar_consulta(consulta):
    """Preprocesa la consulta de la misma forma que los documentos."""
    tokens = tokenizar(consulta)
    tokens = eliminar_stopwords(tokens)
    tokens = eliminar_puntuacion(tokens)
    tokens_reducidos = reducir_palabras(tokens)
    return tokens_reducidos

def calcular_similitud_coseno(query_tokens, indice_invertido, total_docs):
    """Calcula la similitud de coseno entre la consulta y los documentos del indice."""
    tf_query = defaultdict(int)
    for term in query_tokens:
        tf_query[term] += 1  

    query_norm = 0
    for term in tf_query:
        tf_query[term] = math.log10(1 + tf_query[term])
        query_norm += tf_query[term] ** 2
    query_norm = math.sqrt(query_norm)

    doc_scores = defaultdict(float)  
    doc_norms = defaultdict(float)

    for term in query_tokens:
        if term in indice_invertido:
            doc_postings = indice_invertido[term]  
            idf = math.log10(total_docs / len(doc_postings)) 
            
   
            for doc_id in doc_postings:
                tf_doc = doc_postings.count(doc_id)  
                tf_doc = math.log10(1 + tf_doc)
                doc_scores[doc_id] += tf_query[term] * tf_doc * idf
                doc_norms[doc_id] += tf_doc ** 2

    for doc_id in doc_scores:
        doc_norms[doc_id] = math.sqrt(doc_norms[doc_id])
        doc_scores[doc_id] /= (doc_norms[doc_id] * query_norm)

    return dict(sorted(doc_scores.items(), key=lambda item: item[1], reverse=True))

def realizar_consulta(consulta, ruta_json, total_docs=1000, top_k=10):
    """Realiza una consulta sobre el indice invertido y devuelve los documentos mas relevantes."""
    indice_invertido = cargar_indice(ruta_json)
    query_tokens = procesar_consulta(consulta)
    resultados = calcular_similitud_coseno(query_tokens, indice_invertido, total_docs)
    return dict(list(resultados.items())[:top_k])

# Ejemplo de uso
consulta = "boy"
ruta_json = r'C:\Users\semin\OneDrive\Escritorio\bd2\archivo_PROCESADOFinalPe13.json'
top_k_resultados = realizar_consulta(consulta, ruta_json, total_docs=1000, top_k=5)

print(f"Resultados para la consulta '{consulta}':")
for doc_id, score in top_k_resultados.items():
    print(f"Documento: {doc_id}, Similitud: {score}")
    


#ruta_csv = r'C:\Users\semin\OneDrive\Escritorio\bd2\MUEST.csv'
