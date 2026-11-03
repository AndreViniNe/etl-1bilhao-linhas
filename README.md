# ETL performance: Python vs pandas vs DuckDB vs PySpark

A performance comparison of three ways to process a large text file, based on the [One Billion Row Challenge](https://github.com/gunnarmorling/1brc).

The task: read a file of weather station measurements (`station;temperature`, one per line) and compute the **minimum, mean and maximum temperature per station**, sorted by station name.

## Approaches

| Script | Approach |
|---|---|
| `etl-python.py` | Pure Python: reads the file line by line with `csv.reader` and stores the temperatures in a `defaultdict` |
| `etl-pandas.py` | pandas: `read_csv` + `groupby().agg()` |
| `etl-duckdb.py` | DuckDB: a single SQL query directly over the file with `read_csv` |
| `etl-pyspark.py` | PySpark: `spark.read.csv` + `groupBy().agg()`, runnable locally or on Databricks |

## Results

Measured on a **10-million-row file (~152 MB)** on a 2-core machine with 7 GB of RAM:

| Approach | Time |
|---|---|
| Pure Python | ~9.0 s |
| pandas | ~2.4 s |
| **DuckDB** | **~0.8 s** |

**DuckDB was about 11× faster than pure Python.**

### PySpark on Databricks

The same 10-million-row file, processed with `etl-pyspark.py` on **Databricks Free Edition**: **~2.4 s**.

This runs on different hardware from the table above, so the two aren't a direct comparison. The point is the contrast with Spark on a small local machine, where it was the *slowest* option (~12 s on the 2-core machine): starting the JVM and scheduling tasks adds overhead that a single-machine engine like DuckDB doesn't have. On Databricks, the Spark session is already running and the work runs on managed compute, so that overhead disappears.

## Why the results differ

- **Pure Python** processes one row at a time in the interpreter and keeps every value in memory, so it's the slowest and its memory use grows with the data.
- **pandas** is vectorized, so it's much faster, but it runs on a single thread and loads the **whole file into memory**. At a billion rows, it wouldn't fit in a normal machine's RAM.
- **DuckDB** is a columnar, vectorized, multi-threaded SQL engine that streams the file, so it uses all CPU cores and doesn't need the data to fit in memory.

- **PySpark** is a distributed engine: it splits the file into partitions, processes them in parallel and shuffles rows by station to aggregate. Its transformations are *lazy*: nothing runs until an action like `.show()`. On one small machine, that machinery is overhead; its strength is scaling out across a cluster when the data no longer fits on one machine.

**Takeaway:** for data that fits on one machine, DuckDB is hard to beat. When it doesn't, Spark spreads the work across a cluster, and that's where a platform like Databricks comes in.

## Dashboard

The `dashboard/` folder contains a Streamlit app that shows the summary per station:

- `using_duckdb_to_save_parquet.py` computes the summary with DuckDB and saves it to `data/measurements_summary.parquet`.
- `dashboard_certo.py` reads the precomputed Parquet file, so the dashboard loads fast.
- `dashboard_errado.py` recomputes everything from the raw file on every load. It's kept as a counter-example.

## How to run

```bash
poetry install

# 1. Generate the data (100 million rows by default; edit num_rows_to_create to change it)
poetry run python create_measurements.py

# 2. Run each approach
poetry run python etl-python.py
poetry run python etl-pandas.py
poetry run python etl-duckdb.py
poetry run python etl-pyspark.py   # requires pyspark and Java

# On Databricks: upload measurements.txt to a Volume and pass its path:
#   /Volumes/<catalog>/<schema>/<volume>/measurements.txt

# 3. Dashboard
poetry run python dashboard/using_duckdb_to_save_parquet.py
poetry run streamlit run dashboard/dashboard_certo.py
```

The data generator is adapted from the One Billion Row Challenge. The weather station list comes from [simplemaps](https://simplemaps.com/data/world-cities) (CC BY 4.0).
