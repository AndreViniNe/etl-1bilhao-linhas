import time

import pandas as pd

TXT_PATH = "data/measurements.txt"


def process_temperatures(txt_path: str) -> pd.DataFrame:
    print("Iniciando o processamento do arquivo.")
    start_time = time.time()

    df = pd.read_csv(
        txt_path,
        sep=";",
        header=None,
        names=["station", "measure"],
    )

    # Calcula min, média e max por estação e ordena pelo nome da estação
    df_kpi = (
        df.groupby("station")["measure"]
        .agg(["min", "mean", "max"])
        .sort_index()
    )

    print(f"Processamento concluído em {time.time() - start_time:.2f} segundos.")
    return df_kpi


if __name__ == "__main__":
    results = process_temperatures(TXT_PATH)
    print(results)
