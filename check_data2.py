import pandas as pd
df = pd.read_csv('shenzhen_birds.csv')
print(f"Total: {len(df)}, Species: {df['species'].nunique()}")
print(f"Sources: {df['source'].value_counts().to_dict() if 'source' in df.columns else 'source column missing'}")
print()
dist = df.groupby('month').size()
print("Month distribution:")
for m, c in dist.items():
    print(f"  {int(m)}月: {c} records")
print(f"\nSpecies total: {df['species'].nunique()}")
