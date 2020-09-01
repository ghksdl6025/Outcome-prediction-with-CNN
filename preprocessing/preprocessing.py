import pandas as pd
import indexbase_encoding
import math
df = pd.read_csv('../data/trafficfine/indexbase_prefix8.csv')

groups = df.groupby('Case ID')


whatthehack =set()
for col in df.columns.values:
    for k in set(df[col]):
        try:
            if math.isnan(k):
                whatthehack.add(col)
        except:
            pass
print(sorted(list(whatthehack)))