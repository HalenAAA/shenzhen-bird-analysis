"""
合并数据：
- 新 GBIF 全12月数据
- 旧 iNaturalist 数据
"""
import pandas as pd

# 新拉的全12月 GBIF
gbif = pd.read_csv("shenzhen_birds_gbif_full.csv")
gbif["source"] = ""

# 旧数据中的 iNaturalist 部分
old = pd.read_csv("shenzhen_birds.csv")
inat = old[old.get("source", "") == "iNaturalist"]

print(f"New GBIF: {len(gbif)}, iNaturalist: {len(inat)}")

# 合并
combined = pd.concat([gbif, inat], ignore_index=True)
combined.to_csv("shenzhen_birds.csv", index=False, encoding="utf-8-sig")

print(f"Total: {len(combined)} records, {combined['species'].nunique()} species")
dist = combined.groupby("month").size()
for m,c in dist.items():
    src = combined[combined["month"]==m]
    g = len(src[src.get("source","")!="iNaturalist"])
    i = len(src[src.get("source","")=="iNaturalist"])
    print(f"  {int(m):02d}: {c:4d} (GBIF {g:3d} + iNat {i:3d})")
