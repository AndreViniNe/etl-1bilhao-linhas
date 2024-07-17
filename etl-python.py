from csv import reader
from collections import defaultdict
import time

from pathlib import Path

TXT_PATH = "data/measurements.txt"

def process_temperatures(txt_path: Path):
    print("Iniciando o processamento do arquivo.")

    start_time = time.time() #tempo de inicio

    station_temperature = defaultdict(list)

    with open(txt_path, 'r', encoding="utf-8") as file: #open -> gerenciador de contexto (arquivo abre e arquivo fecha)
        _reader = reader(file, delimiter=";")
        for row in _reader:
            station_name, temperature = str(row[0]), float(row[1])
            station_temperature[station_name].append(temperature)
    
    print("Dados carregados! Calculando estatísticas...")

    #Dicionario para armazenar os resultados calculados
    results = {}

    for station, temperatures in station_temperature.items():
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        mean_temp = sum(temperatures)/len(temperatures)
        results[station] = (min_temp, mean_temp, max_temp)

    print("Estatística calculada! Ordenando...")
    #Ordena resultados por nome de estação
    sorted_results = dict(sorted(results.items()))

    formatted_results = {station: f"{min_temp:.1f}/{mean_temp:.1f}/{max_temp:.1f}" for station, (min_temp, mean_temp, max_temp) in sorted_results.items()}

    end_time = time.time() #tempo de término
    print(f"Processamento concluído em {end_time - start_time:.2f} segundos.")

    return formatted_results

if __name__ == "__main__":
    txt_path: Path = Path("data/measurements.txt")
    #100M > 5 minutos
    results = process_temperatures(txt_path)