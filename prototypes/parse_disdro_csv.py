import pandas as pd


b2str = lambda x: x.encode('ascii')

# seperate telegram from datetime and timestamp
df = pd.read_csv('csvs/20231106_PAR007_CabauwTower.csv',
                 sep=';',
                 header=0,
                 names=['datetime', 'timestamp', 'telegram'],
                 converters={'telegram': b2str},
                 parse_dates=['datetime'])
print(df.sample())

# [1439 rows x 3 columns]