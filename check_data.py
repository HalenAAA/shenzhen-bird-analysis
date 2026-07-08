import pandas as pd
df = pd.read_csv('shenzhen_birds.csv')
print(f"Total: {len(df)}, Species: {df['species'].nunique()}, Families: {df['family'].nunique()}")
dist = df.groupby(['year', 'month']).size()
for (y, m), c in dist.items():
    print(f"  {int(y)}-{int(m):02d}: {c} records")
print()
for m in [1, 4, 7, 10]:
    season_df = df[df['month'] == m]
    print(f"Month {m}: {len(season_df)} records, {season_df['species'].nunique()} species")
