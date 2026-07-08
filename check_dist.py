import pandas as pd
df = pd.read_csv('shenzhen_birds.csv')

print("=== Month distribution ===")
monthly = df.groupby('month').agg(
    records=('species','count'),
    species=('species','nunique')
)
for m, row in monthly.iterrows():
    print(f"  {int(m):2d}: {int(row['records']):4d} records, {int(row['species'])} species")

if 'source' in df.columns:
    print("\n=== GBIF only ===")
    gbif = df[df['source'].isna() | (df['source'] == '')]
    for m,c in gbif.groupby('month').size().items():
        print(f"  {int(m):2d}: {c}")

    print("\n=== iNaturalist only ===")
    inat = df[df['source'] == 'iNaturalist']
    for m,c in inat.groupby('month').size().items():
        print(f"  {int(m):2d}: {c}")

print(f"\nTotal: {len(df)} | Species: {df['species'].nunique()}")
