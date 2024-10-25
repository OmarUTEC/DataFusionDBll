"""
import csv
import sys

csv.field_size_limit(2**31 - 1)

input_file = 'C:/data/large_news4.csv'
output_file = 'C:/data/clean_large_news2.csv'  

def clean_text(text):
    return text.encode('ascii', 'ignore').decode('ascii')

with open(input_file, 'r', encoding='windows-1252', errors='replace') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        cleaned_row = [clean_text(col) for col in row]
        writer.writerow(cleaned_row)

print(f"Archivo limpio guardado en: {output_file}")
"""
import matplotlib.pyplot as plt

records_new_case = [50000, 51000, 56000, 58000, 60000, 62000, 64000, 66000, 68000, 70000]
con_indice_new_case = [27.082, 38.304, 284.075, 33.901, 245.546, 55.028, 596.874, 150.871, 45.65, 145.34]
sin_indice_new_case = [18019.444, 25094.294, 25847.626, 25379.883, 23696.992, 27184.138, 27679.162, 22037.871, 24536.234, 21716.122]

plt.figure(figsize=(12, 6))

plt.plot(records_new_case, con_indice_new_case, label='Con índice', marker='o', color='green')
plt.plot(records_new_case, sin_indice_new_case, label='Sin índice', marker='o', color='blue')


plt.xlabel('Records', fontsize=12)
plt.ylabel('Tiempo de ejecución (ms)', fontsize=12)

# Título
plt.title('Comparación de tiempos de ejecución: Con índice vs Sin índice', fontsize=14)

# Leyenda
plt.legend()

plt.grid(True)

# Límites del eje X e Y para ajustar mejor la visualización
plt.xlim(49000, 71000)
plt.ylim(0, max(sin_indice_new_case) * 1.1)

# Mostrar gráfico
plt.show()






