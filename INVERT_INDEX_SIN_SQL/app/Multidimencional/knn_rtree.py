# knn_rtree.py
from rtree import index
import numpy as np
import struct
import pickle

class KNN_R_Tree:
    def __init__(self, n_data: int, load_data: bool):
        self.n_data = n_data
        self.vector_size = 4000
        
        # Configuración RTree
        p = index.Property()
        p.dimension = self.vector_size
        p.buffering_capacity = 8
        p.storage = index.RT_Memory
        self.idx = index.Index(properties=p)
        
        # Cargar datos existentes
        if load_data:
            with open('id_to_pos.bin', 'rb') as f:
                self.id_to_pos = pickle.load(f)
            
        # Construir índice
        for i in range(n_data):
            vector = self.get_vector(i)
            if vector is not None:
                self.idx.insert(i, tuple(vector.tolist() * 2))

    def get_vector(self, id):
        """Obtiene vector desde archivo binario"""
        if id not in self.id_to_pos:
            return None
        position = self.id_to_pos[id]
        with open('output.bin', 'rb') as f:
            f.seek(position)
            data = f.read(4 + self.vector_size * 4)
            return np.array(struct.unpack('i' + 'f' * self.vector_size, data)[1:])

    def knn_search(self, query_id, k=8):
        """Búsqueda de k vecinos más cercanos"""
        query_vector = self.get_vector(query_id)
        if query_vector is None:
            return []
            
        nearest = list(self.idx.nearest(tuple(query_vector.tolist() * 2), num_results=k+1))
        results = []
        
        for id in nearest:
            if id != query_id:
                vector = self.get_vector(id)
                if vector is not None:
                    distance = np.sqrt(np.sum((query_vector - vector) ** 2))
                    results.append({
                        "id": id,
                        "distance": float(distance)
                    })
                    
        return sorted(results, key=lambda x: x['distance'])[:k]

if __name__ == "__main__":
    # Ejemplo de uso
    rtree = KNN_R_Tree(44447, True)
    results = rtree.knn_search(15970, k=8)
    print("\nVecinos más cercanos encontrados:")
    for i, r in enumerate(results, 1):
        print(f"{i}. ID: {r['id']} (Distancia: {r['distance']:.4f})")
