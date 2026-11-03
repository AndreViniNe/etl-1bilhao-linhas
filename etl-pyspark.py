import sys
import time

from pyspark.sql import SparkSession, functions as F

# Caminho do arquivo. Localmente: data/measurements.txt
# No Databricks: um Volume, ex. /Volumes/<catalog>/<schema>/<volume>/measurements.txt
TXT_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/measurements.txt"


def process_temperatures(spark: SparkSession, txt_path: str):
    print("Iniciando o processamento do arquivo.")
    start_time = time.time()

    # Schema explícito: mais rápido do que deixar o Spark inferir os tipos
    df = spark.read.csv(txt_path, sep=";", schema="station STRING, measure DOUBLE")

    # Transformações são LAZY: aqui o Spark só monta o plano de execução
    result = (
        df.groupBy("station")
        .agg(
            F.min("measure").alias("min"),
            F.round(F.avg("measure"), 1).alias("mean"),
            F.max("measure").alias("max"),
        )
        .orderBy("station")
    )

    # Ação: dispara a execução. O Spark divide o arquivo em partições,
    # processa em paralelo e faz o shuffle por estação para agregar
    result.show(10)

    print(f"Spark took {time.time() - start_time:.2f} s")
    return result


if __name__ == "__main__":
    # No Databricks, getOrCreate() reaproveita a sessão `spark` que já existe.
    # Localmente, cria uma sessão usando todos os núcleos (local[*]).
    spark = SparkSession.builder.appName("etl-1bilhao-linhas").getOrCreate()
    process_temperatures(spark, TXT_PATH)
