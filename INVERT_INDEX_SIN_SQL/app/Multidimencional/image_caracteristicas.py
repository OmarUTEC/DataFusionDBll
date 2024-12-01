import re
import requests
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.applications.inception_v3 import preprocess_input
import numpy as np
import gc
import struct
import pandas as pd
import os
import pickle
from tempfile import NamedTemporaryFile
from tqdm import tqdm

# Inicializa el modelo InceptionV3
modelo = InceptionV3(weights='imagenet', include_top=False, pooling='avg')

# Configuración
EXPECTED_LENGTH_DATA = 2048
INTEGER_BYTES = 4
FLOAT_BYTES = 4
VECTOR_SIZE = 4000

# Archivos
images_csv = "images1.csv"
output_file = "output.bin"
position_data_file = "position_data.bin"
id_to_pos_file = "id_to_pos.bin"
state_file = "state.pkl"

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def extract_features_url(image_link):
    try:
        response = requests.get(image_link, stream=True)
        if response.status_code != 200:
            return None

        with NamedTemporaryFile(delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        img = load_img(temp_file_path, target_size=(299, 299))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        features = modelo.predict(img_array, verbose=0).flatten()

        if len(features) > VECTOR_SIZE:
            features = features[:VECTOR_SIZE]
        elif len(features) < VECTOR_SIZE:
            features = np.pad(features, (0, VECTOR_SIZE - len(features)), 'constant')

        os.remove(temp_file_path)
        del img_array
        gc.collect()

        return features
    except Exception as e:
        return None

def load_images(images_csv, output_file, position_data_file, id_to_pos_file, state_file, n=44447):
    id_to_pos = {}
    start_index = 0

    if os.path.exists(state_file):
        with open(state_file, 'rb') as f:
            state = pickle.load(f)
            id_to_pos = state['id_to_pos']
            start_index = state['start_index']
        print(f"Reanudando desde el índice {start_index}")

    if os.path.exists(output_file) and os.path.exists(position_data_file) and os.path.exists(id_to_pos_file):
        with open(id_to_pos_file, 'rb') as f:
            id_to_pos = pickle.load(f)
        return id_to_pos

    with open(output_file, 'ab') as file, open(position_data_file, "ab") as position_data:
        # Leer CSV sin modificar el orden original
        df_images = pd.read_csv(images_csv)
        
        # Verificar primera imagen
        primera_imagen = df_images.iloc[0]['filename']
        print(f"\nPrimera imagen en CSV: {primera_imagen}")
        
        total = len(df_images)
        pbar = tqdm(total=total)
        
        for i, row in enumerate(df_images.iterrows()):
            if i < start_index:
                pbar.update(1)
                continue
            if n and i >= n:
                break

            _, row = row
            image_link = row['link']
            image_name = row['filename']
            
            pbar.set_description(f"Procesando imagen: {image_name}")
            print(f"\nProcesando: {image_name}")
            
            try:
                position_seek = file.tell()
                img_encoding = extract_features_url(image_link)
                
                if img_encoding is not None and len(img_encoding) == VECTOR_SIZE:
                    id = i
                    id_to_pos[id] = position_seek
                    data = struct.pack('i' + 'f' * len(img_encoding), id, *img_encoding)
                    file.write(data)
                    position_data.write(struct.pack('ii', id, position_seek))

                    if i % 100 == 0:
                        with open(state_file, 'wb') as f:
                            pickle.dump({'id_to_pos': id_to_pos, 'start_index': i + 1}, f)
                            
            except Exception as e:
                print(f"\nError en imagen {image_name}: {str(e)}")
                continue
            
            pbar.update(1)
        
        pbar.close()

    with open(state_file, 'wb') as f:
        pickle.dump({'id_to_pos': id_to_pos, 'start_index': i + 1}, f)

    with open(id_to_pos_file, 'wb') as f:
        pickle.dump(id_to_pos, f)

    return id_to_pos

def mostrar_estado_procesamiento():
    if os.path.exists(state_file):
        with open(state_file, 'rb') as f:
            state = pickle.load(f)
            total = len(pd.read_csv(images_csv))
            procesadas = state['start_index']
            print(f"\nProgreso: {procesadas}/{total} ({(procesadas/total)*100:.2f}%)")

if __name__ == "__main__":
    print("Iniciando proceso de extracción de características...")
    id_to_pos = load_images(images_csv, output_file, position_data_file, id_to_pos_file, state_file)
    mostrar_estado_procesamiento()
    print("\nProceso completado.")
