import pandas as pd

df = pd.read_csv('./data/BPIC15_2prep.csv')
df['Complete Timestamp'] = pd.to_datetime(df['Complete Timestamp'])
prefix = 5

groups = df.groupby('Case ID')

prefixedlog=[]
for case, group in groups:
    if len(group) >prefix:
        group = group.sort_values(by='Complete Timestamp')
        prefixedlog.append(group.iloc[:prefix,:])

dfn = pd.concat(prefixedlog)
dfn_name = 'BPIC2015_2prep_prefix'+str(prefix)+'.csv'
dfn.to_csv('../data/'+dfn_name,index=False)


