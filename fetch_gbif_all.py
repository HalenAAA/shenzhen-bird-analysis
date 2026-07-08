"""
拉取 GBIF 全年12个月数据（2025年），每月约500条
"""
import requests, pandas as pd, time, os

LAT_MIN, LAT_MAX = 22.45, 22.87
LON_MIN, LON_MAX = 113.75, 114.65
TAXON_KEY_AVES = 212
PROXIES = {}
if os.environ.get("HTTP_PROXY"): PROXIES = {"http": os.environ["HTTP_PROXY"], "https": os.environ["HTTPS_PROXY"]}

def fetch_month(year, month, limit=500):
    all_records, offset = [], 0
    url = "https://api.gbif.org/v1/occurrence/search"
    while offset < limit:
        params = {"taxonKey": TAXON_KEY_AVES, "decimalLatitude": f"{LAT_MIN},{LAT_MAX}",
                  "decimalLongitude": f"{LON_MIN},{LON_MAX}",
                  "year": str(year), "month": str(month), "limit": 300, "offset": offset}
        try:
            resp = requests.get(url, params=params, timeout=60, proxies=PROXIES)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if not results: break
            all_records.extend(results); offset += len(results)
            time.sleep(0.3)
        except Exception as e:
            print(f"  {year}-{month:02d} ERR: {e}"); break
    return all_records

if __name__ == "__main__":
    all_records = []
    for m in range(1, 13):
        print(f"Fetching 2025-{m:02d}...", end=" ")
        recs = fetch_month(2025, m, limit=500)
        print(f"{len(recs)} records")
        all_records.extend(recs)

    df = pd.json_normalize(all_records).dropna(subset=["species"])
    keep = ["species","genus","family","order","year","month","day",
            "decimalLatitude","decimalLongitude","locality","county",
            "individualCount","basisOfRecord","datasetName","institutionCode"]
    keep = [c for c in keep if c in df.columns]
    df = df[keep]
    df.to_csv("shenzhen_birds_gbif_full.csv", index=False, encoding="utf-8-sig")
    print(f"\nSaved: {len(df)} records from {df['year'].min()} to {df['year'].max()}")
    dist = df.groupby("month").size()
    for m,c in dist.items(): print(f"  {int(m):02d}: {c}")
