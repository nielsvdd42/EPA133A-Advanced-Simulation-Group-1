import pandas as pd
import numpy as np

df1 = pd.read_csv('_roads3.csv')
# print(df1.head())

dfN1 = df1[df1['road'] == 'N1']
# print(dfN1.tail())
dfN1['chainage'] = pd.to_numeric(dfN1['chainage'], errors='coerce')

source_val = 0
sink_val = dfN1['chainage'].max()
source_row = dfN1[dfN1['chainage'] == source_val].head(1)
sink_row = dfN1[dfN1['chainage'] == sink_val].head(1)

bridges = dfN1[dfN1['type'].str.contains('Bridge', na=False, case=False)].copy()
df_proc = pd.concat([source_row, bridges, sink_row]).drop_duplicates(subset=['chainage', 'lrp']).sort_values('chainage').reset_index(drop=True)

def filter_bridge_name(row):
    if row['chainage'] == source_val or row['chainage'] == sink_val:
        return True

    return 'bridge' in str(row['name']).lower()

df_proc = df_proc[df_proc.apply(filter_bridge_name, axis=1)].reset_index(drop=True)
# print(df_proc.describe())
# print(df_proc['name'].value_counts())

def identify_marker(row):
    n = str(row['name']).lower()
    g = str(row['gap']).upper()
    if 'bridge start' in n or g == 'BS': return 'BS'
    if 'bridge end' in n or g == 'BE': return 'BE'
    return None

df_proc['gap_fixed'] = df_proc.apply(identify_marker, axis=1)

mask_ends = df_proc['chainage'].isin([source_val, sink_val])
df_proc.loc[mask_ends, 'gap_fixed'] = pd.NA

print(df_proc['gap_fixed'].value_counts())
print(df_proc['gap'].value_counts())
print(df_proc['gap_fixed'].head(50))
print(df_proc.iloc[18])

# for i in range(1, len(df_proc)):
#     if pd.isna(df_proc.loc[i, 'gap_fixed']):
#         prev_name = str(df_proc.loc[i - 1, 'name']).lower()
#         if 'bridge end' in prev_name:
#             df_proc.loc[i, 'gap_fixed'] = 'BS'
#         elif df_proc.loc[i - 1, 'gap_fixed'] == 'BE':
#             df_proc.loc[i, 'gap_fixed'] = 'BS'
#         elif df_proc.loc[i - 1, 'gap_fixed'] == 'BS':
#             df_proc.loc[i, 'gap_fixed'] = 'BE'

for i in range(1, len(df_proc)):
    # sla source en sink over
    if df_proc.loc[i, 'chainage'] in (source_val, sink_val):
        continue

    if pd.isna(df_proc.loc[i, 'gap_fixed']):
        prev_gap = df_proc.loc[i - 1, 'gap_fixed']
        prev_name = str(df_proc.loc[i - 1, 'name']).lower()

        if 'bridge end' in prev_name:
            df_proc.loc[i, 'gap_fixed'] = 'BS'
        elif prev_gap == 'BE':
            df_proc.loc[i, 'gap_fixed'] = 'BS'
        elif prev_gap == 'BS':
            df_proc.loc[i, 'gap_fixed'] = 'BE'

df_proc['gap'] = df_proc['gap_fixed']
print(df_proc['gap_fixed'].tail(5))

df_proc['model_type'] = ''
for i, row in df_proc.iterrows():
    if row['chainage'] == source_val:
        df_proc.at[i, 'model_type'] = 'source'

    elif row['chainage'] == sink_val:
        df_proc.at[i, 'model_type'] = 'sink'

    elif row['gap'] == 'BS':
        df_proc.at[i, 'model_type'] = 'bridge'

    elif row['gap'] == 'BE':
        df_proc.at[i, 'model_type'] = 'link'


print(df_proc['model_type'].value_counts())
print(df_proc.head(10))


df_proc['length'] = 0.0

for i in range(len(df_proc) - 1):
    df_proc.at[i, 'length'] = df_proc.at[i+1, 'chainage'] - df_proc.at[i, 'chainage']


# print(df_proc.head(10))

dfBMMS = pd.read_excel('BMMS_overview.xlsx')
# print(df_BMMS.head(20))
bridges_BMMS = dfBMMS[dfBMMS['type'].str.contains('Bridge', na=False, case=False)].copy()
# print(bridges_BMMS.describe())
cols = [
    "road",
    "LRPName",
    "name",
    "length",
    "chainage",
    "lat",
    "lon",
    "condition",
]

bridges_BMMS2 = bridges_BMMS[cols].copy()

bridges_BMMS_N1 = bridges_BMMS2[
    bridges_BMMS2['road'].str.upper() == 'N1'
].copy()

bridges_BMMS_N1= bridges_BMMS_N1.drop_duplicates(
    subset=["lat", "lon"],
    keep="first"
).copy()
print(bridges_BMMS_N1.head(10))

df_proc_bridges = df_proc[df_proc['model_type'] == 'bridge'].copy()
print(df_proc_bridges.head(10))

df_proc['lrp_clean'] = df_proc['lrp'].astype(str).str.strip().str.upper()
bridges_BMMS_N1['lrp_clean'] = bridges_BMMS_N1['LRPName'].astype(str).str.strip().str.upper()

df_proc_bridges = df_proc[df_proc['model_type'] == 'bridge'].copy()
# print(df_proc_bridges['lrp_clean'].value_counts())
# print(bridges_BMMS_N1['lrp_clean'].value_counts())

df_proc_bridges = df_proc_bridges.merge(
    bridges_BMMS_N1[['lrp_clean', 'condition']],
    on='lrp_clean',
    how='left'
)

print(df_proc_bridges.head(10))

df_proc['condition'] = pd.NA

df_proc.loc[
    df_proc['model_type'] == 'bridge',
    'condition'
] = df_proc_bridges['condition'].values

df_proc['model_type'].value_counts()
df_proc[df_proc['model_type'] == 'bridge']['condition'].value_counts(dropna=False)

df_proc = df_proc.reset_index(drop=True)

df_proc['id'] = 100000 + (df_proc.index + 1)

final_cols = [
    'road',
    'id',
    'model_type',
    'name',
    'lat',
    'lon',
    'length',
    'condition'
]

df_final = df_proc[final_cols].copy()

print(df_final.head(15))

df_final.to_csv('processed_roads_N1.csv', index=False)








