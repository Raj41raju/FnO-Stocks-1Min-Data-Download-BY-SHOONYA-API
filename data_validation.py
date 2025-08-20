import dask.dataframe as dd

# Read parquet file
df = dd.read_parquet("TATAMOTORS.parquet")

print(df.head())   # loads only small chunk
