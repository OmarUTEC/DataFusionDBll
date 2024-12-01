import struct
import numpy as np
import heapq
import pandas as pd
import json
import os
import pickle

class KNNSecuencial:
    def __init__(self):
        # Archivos del sistema
        self.binary_file = "output.bin"
        self.position_data_file = "position_data.bin"
        self.id_to_pos_file = "id_to_pos.bin"
        self.csv_file = "images1.csv"
        self.vector_size = 4000
        
        # Cargar datos necesarios
        with open(self.id_to_pos_file, 'rb') as f:
            self.id_to_pos = pickle.load(f)
        self.df_images = pd.read_csv(self.csv_file)

    def get_vector(self, id):
        """Obtiene vector de características desde archivo binario"""
        if id not in self.id_to_pos:
            return None
        position = self.id_to_pos[id]
        with open(self.binary_file, 'rb') as f:
            f.seek(position)
            data = f.read(4 + self.vector_size * 4)
            vector = np.array(struct.unpack('i' + 'f' * self.vector_size, data)[1:])
        return vector

    def euclidean_distance(self, x, y):
        """Calcula distancia euclidiana entre vectores"""
        return np.sqrt(np.sum((x - y) ** 2))

    def knn_search(self, query_id, k=8):
        """Búsqueda de k vecinos más cercanos"""
        query_vector = self.get_vector(query_id)
        if query_vector is None:
            return []
            
        heap = []
        processed = set()
        
        for id in self.id_to_pos.keys():
            vector = self.get_vector(id)
            if vector is not None:
                distance = self.euclidean_distance(query_vector, vector)
                if id not in processed:
                    heapq.heappush(heap, (-distance, id))
                    processed.add(id)
                    if len(heap) > k:
                        heapq.heappop(heap)

        results = []
        for dist, id in sorted(heap, key=lambda x: -x[0]):
            row = self.df_images.iloc[id]
            results.append({
                "Index": int(id),
                "Filename": row['filename'],
                "Distance": float(-dist),
                "Link": row['link']
            })
        return results

    def save_neighbors_to_json(self, query_id, filename="neighbors.json"):
        """Guarda resultados en formato JSON"""
        neighbors = self.knn_search(query_id)
        with open(filename, 'w') as json_file:
            json.dump(neighbors, json_file, indent=4)
        print(f"Vecinos más cercanos guardados en: {filename}")
        return neighbors

def find_image_index(df, image_name):
    """Encuentra índice de una imagen en el DataFrame"""
    matches = df[df['filename'] == image_name]
    if not matches.empty:
        return matches.index[0]
    return None

if __name__ == "__main__":
    knn = KNNSecuencial()
    
    # Imagen de prueba
    test_image = "55370.jpg"
    test_index = find_image_index(knn.df_images, test_image)
    
    if test_index is not None:
        print(f"Buscando vecinos más cercanos para: {test_image}")
        results = knn.save_neighbors_to_json(test_index, "test_neighbors.json")
        
        # Mostrar resultados
        print("\nVecinos más cercanos encontrados:")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['Filename']} (Distancia: {r['Distance']:.4f})")
    else:
        print(f"Error: Imagen {test_image} no encontrada en el dataset")
