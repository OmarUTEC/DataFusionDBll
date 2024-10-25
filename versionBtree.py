import csv
import nltk
import json
from collections import defaultdict

class BPlusTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []  # Lista de términos
        self.children = []  # Punteros a hijos (o registros)

class BPlusTree:
    def __init__(self, t=3):  # Grado t del árbol
        self.root = BPlusTreeNode(leaf=True)
        self.t = t

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == (2 * self.t - 1):
            new_node = BPlusTreeNode()
            self.root = new_node
            new_node.children.append(root)
            self.split_child(new_node, 0, root)
            self._insert_non_full(new_node, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _insert_non_full(self, node, key, value):
        if node.leaf:
            if key not in node.keys:
                node.keys.append(key)
                node.children.append([value])
            else:
                idx = node.keys.index(key)
                if value not in node.children[idx]:
                    node.children[idx].append(value)
            node.keys.sort()
        else:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t - 1):
                self.split_child(node, i, node.children[i])
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def split_child(self, parent, index, node):
        new_node = BPlusTreeNode(leaf=node.leaf)
        parent.keys.insert(index, node.keys[self.t - 1])
        parent.children.insert(index + 1, new_node)

        new_node.keys = node.keys[self.t:(2 * self.t - 1)]
        node.keys = node.keys[0:(self.t - 1)]

        if not node.leaf:
            new_node.children = node.children[self.t:(2 * self.t)]
            node.children = node.children[0:self.t]

    def search(self, key):
        current_node = self.root
        while not current_node.leaf:
            i = 0
            while i < len(current_node.keys) and key > current_node.keys[i]:
                i += 1
            current_node = current_node.children[i]
        if key in current_node.keys:
            return current_node.children[current_node.keys.index(key)]
        else:
            return None

def tokenizar(texto):
    palabras = nltk.word_tokenize(texto.lower())
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

def Procesing(documento):
    tokens = tokenizar(documento)
    tokens = eliminar_stopwords(tokens)
    return tokens

def ReadCSVWithBPlusTree(ruta_csv, sizeBuffer, ruta_json):
    bplustree = BPlusTree(t=3)  # Creamos un árbol B+ de grado 3
    with open(ruta_csv, 'r', encoding='utf-8') as archivo:
        encabezado = archivo.readline()  # Leer y descartar el encabezado
        buffer = []
        buffer_id = 1
        for linea in archivo:
            buffer.append(linea.strip())
            if len(buffer) == sizeBuffer:
                for documento in buffer:
                    doc_id = f"buffer_{buffer_id}_doc_{buffer.index(documento) + 1}"
                    tokens = Procesing(documento)
                    for token in tokens:
                        bplustree.insert(token, doc_id)
                buffer = []
                buffer_id += 1

        if buffer:
            for documento in buffer:
                doc_id = f"buffer_{buffer_id}_doc_{buffer.index(documento) + 1}"
                tokens = Procesing(documento)
                for token in tokens:
                    bplustree.insert(token, doc_id)

    # Convertir la estructura del árbol B+ a un formato JSON para almacenamiento
    def bplustree_to_dict(node):
        if node.leaf:
            return {key: value for key, value in zip(node.keys, node.children)}
        else:
            return {key: bplustree_to_dict(child) for key, child in zip(node.keys, node.children)}

    with open(ruta_json, 'w', encoding='utf-8') as archivo_json:
        json.dump(bplustree_to_dict(bplustree.root), archivo_json, indent=4, ensure_ascii=False)

# Llamar a la función con la ruta y el tamaño del buffer deseado
#ruta_csv = r'C:\Users\semin\OneDrive\Escritorio\bd2\archivo_simplificado.csv'
ruta_csv = r'C:\Users\semin\OneDrive\Escritorio\bd2\Documento.csv'
sizeBuffer = 10
ruta_json = r'C:\Users\semin\OneDrive\Escritorio\bd2\archivo_PROCESADO_BPlusTree.json'

ReadCSVWithBPlusTree(ruta_csv, sizeBuffer, ruta_json)
