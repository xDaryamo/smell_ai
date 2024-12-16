import pandas as pd

def merge_dataframes(df1, df2):
    result = df1.merge(df2)  # Manca esplicitazione di `how`, `on`, e `validate`
    return result
