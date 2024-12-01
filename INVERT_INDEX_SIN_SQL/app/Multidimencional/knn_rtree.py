# rtree_builder.py
import numpy as np
from rtree import index
import struct
import pandas as pd
import json
import pickle
from tqdm import tqdm
from sklearn.cluster import KMeans

class KNNRTreeLocal:
    def get_vector_original(self, id):
        if id not in self.id_to_pos:
            return None
        position = self.id_to_pos[id]
        with open(self.binary_file, 'rb') as f:
            f.seek(position)
            data = f.read(4 + self.vector_size * 4)
            return np.array(struct.unpack('i' + 'f' * self.vector_size, data)[1:])

    def __init__(self, n_data=44447, n_clusters=100):
        self.n_data = n_data
        self.binary_file = "output.bin"
        self.id_to_pos_file = "id_to_pos.bin"
        self.csv_file = "images1.csv"
        self.vector_size = 4000
        self.n_clusters = n_clusters

        # Configuración RTree
        p = index.Property()
        p.dimension = self.n_clusters
        p.buffering_capacity = 8
        p.storage = index.RT_Memory
        self.idx = index.Index(properties=p)

        # Cargar datos
        with open(self.id_to_pos_file, 'rb') as f:
            self.id_to_pos = pickle.load(f)
        self.df_images = pd.read_csv(self.csv_file)

        # Inicializar índice invertido
        self.inverted_index = {}
        
        vectors = []
        self.valid_indices = []
        
        for i in tqdm(range(self.n_data), desc="Cargando vectores"):
            vector = self.get_vector_original(i)
            if vector is not None:
                vectors.append(vector)
                self.valid_indices.append(i)
        
    
        print("\nCreando descriptores locales con K-means.")
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.descriptors = self.kmeans.fit_transform(vectors)
        
        # Construir índices
        self._build_index()
        self._build_inverted_index()

    def _build_index(self):
        print("\nConstruyendo índice RTree...")
        try:
            vectores_insertados = 0
            
            for i, descriptor in enumerate(tqdm(self.descriptors, desc="Procesando")):
                self.idx.insert(self.valid_indices[i], tuple(descriptor.tolist() * 2))
                vectores_insertados += 1
                
    
            total_elementos = len(self.idx.leaves())
            print("\nEstadísticas del índice RTree:")
            print(f"- Vectores insertados: {vectores_insertados}")
            print(f"- Total de nodos hoja: {total_elementos}")
            print(f"- Número de clusters: {self.n_clusters}")
            
            return True
            
        except Exception as e:
            print(f"\nError en la construcción del índice: {str(e)}")
            return False

    def _build_inverted_index(self):
        print("\nConstruyendo índice invertido...")
        for i, descriptor in enumerate(self.descriptors):
            cluster = np.argmin(descriptor)
            if cluster not in self.inverted_index:
                self.inverted_index[cluster] = []
            self.inverted_index[cluster].append(self.valid_indices[i])
        print(f"Índice invertido construido con {len(self.inverted_index)} clusters")

    def knn_search(self, query_id, k=8):
        query_vector = self.get_vector_original(query_id)
        if query_vector is None:
            return []
            
        query_descriptor = self.kmeans.transform([query_vector])[0]
        query_cluster = np.argmin(query_descriptor)
        
      
        candidate_ids = self.inverted_index.get(query_cluster, [])
        
        results = []
        for id in candidate_ids:
            if id != query_id:
                vector = self.get_vector_original(id)
                if vector is not None:
                    distance = np.sqrt(np.sum((query_vector - vector) ** 2))
                    row = self.df_images.iloc[id]
                    results.append({
                        "Index": int(id),
                        "Filename": row['filename'],
                        "Distance": float(distance),
                        "Link": row['link']
                    })
                    
        results = sorted(results, key=lambda x: x['Distance'])[:k]
        return results

    def save_neighbors_to_json(self, query_id, filename="neighbors_rtree_local.json"):
        neighbors = self.knn_search(query_id)
        with open(filename, 'w') as json_file:
            json.dump(neighbors, json_file, indent=4)
        return neighbors

def save_index(rtree, filename="rtree_index.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(rtree, f)
    print(f"Índice guardado en {filename}")

def load_index(filename="rtree_index.pkl"):
    with open(filename, 'rb') as f:
        return pickle.load(f)
    


if __name__ == "__main__":
    try:
        # Verificar si existe índice guardado
        try:
            print("Intentando cargar índice existente...")
            rtree = load_index()
            print("Índice cargado exitosamente")
        except:
            print("Construyendo nuevo índice...")
            rtree = KNNRTreeLocal()
            save_index(rtree)
        
        test_image = "12544.jpg"
        test_index = rtree.df_images[rtree.df_images['filename'] == test_image].index[0]
        
        if test_index is not None:
            print(f"\nBuscando 8 vecinos más cercanos para: {test_image}")
            results = rtree.save_neighbors_to_json(test_index)
            
            print("\nVecinos más cercanos encontrados:")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['Filename']} (Distancia: {r['Distance']:.4f})")
        else:
            print(f"Error: Imagen {test_image} no encontrada")
            
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")
