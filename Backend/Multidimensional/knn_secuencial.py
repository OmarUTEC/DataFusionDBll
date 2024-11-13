import struct
import numpy as np
import heapq
import csv
import pandas as pd
import matplotlib.pyplot as plt

VECTOR_SIZE = 2048
BINARY_FILE = 'vectors.bin'
URL_CSV_FILE = 'images1.csv'  

class knnsecuencial:
    def __init__(self, vector_size=VECTOR_SIZE, binary_file=BINARY_FILE, url_csv_file=URL_CSV_FILE):
        self.vector_size = vector_size
        self.binary_file = binary_file
        self.url_csv_file = url_csv_file
        self.vectors = []
        self.url_map = pd.read_csv(url_csv_file) 
    
    def load_vectors(self):
        self.vectors = []
        with open(self.binary_file, 'rb') as f:
            while True:
                data = f.read(4 + 4 * self.vector_size)
                if not data:
                    break
                index = struct.unpack('i', data[:4])[0]
                vector = struct.unpack(f'{self.vector_size}f', data[4:])
                self.vectors.append((index, np.array(vector)))  # Guardar como (index, vector)
        print(f"Se han cargado {len(self.vectors)} vectores desde el archivo binario.")
        return self.vectors
    
    @staticmethod
    def euclidean_distance(x, y):
        return np.sqrt(np.sum((x - y) ** 2))
    
    def calculate_all_pairwise_distances(self):
        
        distances = []
        n = len(self.vectors)
        for i in range(n):
            for j in range(i + 1, n):
                dist = self.euclidean_distance(self.vectors[i][1], self.vectors[j][1])
                distances.append(dist)
        return distances
    
    def analyze_global_distances(self):
        
        distances = self.calculate_all_pairwise_distances()
        median_distance = np.median(distances)
        p75_distance = np.percentile(distances, 75)
        p90_distance = np.percentile(distances, 90)
        
        return [median_distance, p75_distance, p90_distance]  
    
    def knn_range_search(self, query, radius):
        neighbors = []
        for index, vector in self.vectors:
            distance = self.euclidean_distance(vector, query)
            if distance <= radius:
                row = self.url_map.iloc[index]
                filename = row['filename']
                url = row['link']
                neighbors.append((index, filename, distance, radius, url))
        return neighbors
    
    def knn_search_linear(self, query, k):
        heap = []
        unique_neighbors = set()  # Conjunto para evitar vecinos duplicados en el heap
    
        for index, vector in self.vectors:
            distance = self.euclidean_distance(vector, query)
        
        # Solo agregar al heap si el índice no ha sido visto antes
        if index not in unique_neighbors:
            heapq.heappush(heap, (-distance, index))
            unique_neighbors.add(index)  
            if len(heap) > k:
                removed = heapq.heappop(heap)
                unique_neighbors.remove(removed[1]) 
    
        neighbors = []
        for dist, index in sorted(heap, reverse=True):
            row = self.url_map.iloc[index]
            filename = row['filename']
            url = row['link']
            neighbors.append((index, filename, -dist, url))
    
        return neighbors
    
    def save_radius_neighbors_to_csv(self, query, recommended_radii, filename="neighbors_radius.csv"):
        with open(filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Radius", "Index", "Filename", "Distance", "Link"])  
            for radius in recommended_radii:
                neighbors = self.knn_range_search(query, radius)
                if neighbors:
                    for neighbor in neighbors:
                        writer.writerow([radius] + list(neighbor))  
                else:
                    writer.writerow([radius, "No hay vecinos", "No hay vecinos", "No hay vecinos", "No hay vecinos"]) 

    def save_priority_neighbors_to_csv(self, query, k, filename="neighbors_priority.csv"):
        neighbors = self.knn_search_linear(query, k)
        with open(filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Index", "Filename", "Distance", "Link"])  
            for neighbor in neighbors:
                writer.writerow(neighbor)


knn_seq = knnsecuencial()
knn_seq.load_vectors()

query_vector = np.random.rand(VECTOR_SIZE).astype(np.float32)

recommended_radii = knn_seq.analyze_global_distances()
knn_seq.save_radius_neighbors_to_csv(query_vector, recommended_radii)

k = 8 
knn_seq.save_priority_neighbors_to_csv(query_vector, k)

print("\nLos resultados de ambas búsquedas se han guardado en 'neighbors_radius.csv' y 'neighbors_priority.csv'")
