import pandas as pd

df = pd.read_csv("data/measurements.txt", 
                 sep=";",
                 header=None,
                 names=['station', 'measure']
            )

print(df)
df_agg = df.groupby("station")
df_kpi = df_agg['measure'].agg({
        'min': 'min',
        'mean': 'mean',
        'max': 'max'
    })

df_sort = df_kpi.sort_values('station')