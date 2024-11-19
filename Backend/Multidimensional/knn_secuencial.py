import struct
import numpy as np
import heapq
import csv
import pandas as pd
import matplotlib.pyplot as plt

VECTOR_SIZE = 2048
BINARY_FILE = 'output.bin'
POSITION_DATA_FILE = 'position_data.bin'
URL_CSV_FILE = 'images1.csv'
BATCH_SIZE = 1000  # Tamaño del lote

class knnsecuencial:
    def __init__(self, vector_size=VECTOR_SIZE, binary_file=BINARY_FILE, position_data_file=POSITION_DATA_FILE, url_csv_file=URL_CSV_FILE):
        self.vector_size = vector_size
        self.binary_file = binary_file
        self.position_data_file = position_data_file
        self.url_csv_file = url_csv_file
        self.url_map = pd.read_csv(url_csv_file)
        self.distancias = {}
        self.vectors = []
        self.positions = self.load_positions()

    def load_positions(self):
        positions = []
        with open(self.position_data_file, 'rb') as f:
            while True:
                data = f.read(4)
                if not data:
                    break
                position = struct.unpack('i', data)[0]
                positions.append(position)
        return positions

    def euclidean_distance(self, x, y):
        return np.sqrt(np.sum((x - y) ** 2))

    def get_vector(self, index):
        position = self.positions[index]
        with open(self.binary_file, 'rb') as f:
            f.seek(position)
            data = f.read(4 + 4 * self.vector_size)
            if len(data) < 4 + 4 * self.vector_size:
                return None
            vector = np.array(struct.unpack(f'{self.vector_size}f', data[4:]))
        return vector

    def process_batches(self, query, process_function):
        for index in range(len(self.positions)):
            vector = self.get_vector(index)
            if vector is not None:
                process_function(index, vector, query)

    def knn_range_search(self, query, radius):
        neighbors = []
        seen_indices = set()  

        def process_function(index, vector, query):
            distance = self.euclidean_distance(vector, query)
            if distance <= radius and index not in seen_indices:
                seen_indices.add(index)
                if index < len(self.url_map):  
                    row = self.url_map.iloc[index]
                    filename = row['filename']
                    url = row['link']
                    neighbors.append((index, filename, distance, radius, url))
                else:
                    print(f"Índice {index} fuera de rango para el DataFrame")

        self.process_batches(query, process_function)
        return neighbors

    def knn_search_linear(self, query, k):
        heap = []
        unique_neighbors = set() 

        def process_function(index, vector, query):
            distance = self.euclidean_distance(vector, query)
            if index not in unique_neighbors:
                unique_neighbors.add(index)
                heapq.heappush(heap, (-distance, index))
                if len(heap) > k:
                    removed = heapq.heappop(heap)
                    unique_neighbors.remove(removed[1])

        self.process_batches(query, process_function)

        neighbors = []
        for dist, index in sorted(heap, reverse=True):
            if index < len(self.url_map):  
                row = self.url_map.iloc[index]
                filename = row['filename']
                url = row['link']
                neighbors.append((index, filename, -dist, url))
            else:
                print(f"Índice {index} fuera de rango para el DataFrame")

        return neighbors

    def calculate_all_pairwise_distances(self):
        distances = []
        vectors = []


        for index in range(len(self.positions)):
            vector = self.get_vector(index)
            if vector is not None:
                vectors.append((index, vector))

        n = len(vectors)
        for i in range(n):
            for j in range(i + 1, n):
                dist = self.euclidean_distance(vectors[i][1], vectors[j][1])
                distances.append(dist)
        return distances

    def analyze_global_distances(self):
        distances = self.calculate_all_pairwise_distances()
        median_distance = np.median(distances)
        p75_distance = np.percentile(distances, 75)
        p90_distance = np.percentile(distances, 90)
        return [median_distance, p75_distance, p90_distance]

    def save_radius_neighbors_to_csv(self, query, recommended_radii, filename="neighbors_radius.csv"):
        with open(filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Radius", "Index", "Filename", "Distance", "Link"])
            for radius in recommended_radii:
                neighbors = self.knn_range_search(query, radius)
                seen_indices = set() 
                if neighbors:
                    for neighbor in neighbors:
                        if neighbor[0] not in seen_indices:
                            seen_indices.add(neighbor[0])
                            writer.writerow([radius] + list(neighbor))
                else:
                    writer.writerow([radius, "No hay vecinos", "No hay vecinos", "No hay vecinos", "No hay vecinos"])

    def save_priority_neighbors_to_csv(self, query, k, filename="neighbors_priority.csv"):
        neighbors = self.knn_search_linear(query, k)
        with open(filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Index", "Filename", "Distance", "Link"])
            seen_indices = set() 
            for neighbor in neighbors:
                if neighbor[0] not in seen_indices:
                    seen_indices.add(neighbor[0])
                    writer.writerow(neighbor)

# Crear una instancia de knnsecuencial
knn_seq = knnsecuencial()

# Generar un vector de consulta aleatorio
query_vector = np.random.rand(VECTOR_SIZE).astype(np.float32)

# Analizar distancias globales y guardar vecinos por radio en un archivo CSV
recommended_radii = knn_seq.analyze_global_distances()
knn_seq.save_radius_neighbors_to_csv(query_vector, recommended_radii)

# Buscar los k vecinos más cercanos y guardar los resultados en un archivo CSV
k = 8
knn_seq.save_priority_neighbors_to_csv(query_vector, k)

print("\nLos resultados de ambas búsquedas se han guardado en 'neighbors_radius.csv' y 'neighbors_priority.csv'")
