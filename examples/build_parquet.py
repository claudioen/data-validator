import pandas as pd

df = pd.read_csv("examples/customers.csv")
df.to_parquet("examples/customers.parquet", index=False)
print("Wrote examples/customers.parquet")
