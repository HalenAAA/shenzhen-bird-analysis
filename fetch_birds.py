"""
深圳鸟类观测数据拉取 —— 按月拉取，覆盖全年各季
"""
import requests
import pandas as pd
import time
import os

LAT_MIN, LAT_MAX = 22.45, 22.87
LON_MIN, LON_MAX = 113.75, 114.65
TAXON_KEY_AVES = 212

PROXIES = {}
if os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY"):
    PROXIES = {"http": os.environ.get("HTTP_PROXY", ""), "https": os.environ.get("HTTPS_PROXY", "")}


def fetch_month(year, month, limit=1000):
    """拉取某年某月的深圳鸟类数据"""
    all_records = []
    offset = 0
    url = "https://api.gbif.org/v1/occurrence/search"

    while offset < limit:
        params = {
            "taxonKey": TAXON_KEY_AVES,
            "decimalLatitude": f"{LAT_MIN},{LAT_MAX}",
            "decimalLongitude": f"{LON_MIN},{LON_MAX}",
            "year": str(year),
            "month": str(month),
            "limit": 300,
            "offset": offset,
        }
        try:
            resp = requests.get(url, params=params, timeout=60, proxies=PROXIES)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
            all_records.extend(results)
            offset += len(results)
            time.sleep(0.3)
        except Exception as e:
            break

    return all_records


if __name__ == "__main__":
    # 策略：每个季节选一个代表月，各拉 1500 条
    schedule = [
        (2025, 1),   # 冬季
        (2025, 4),   # 春季
        (2025, 7),   # 夏季
        (2025, 10),  # 秋季
    ]

    all_records = []
    for year, month in schedule:
        print(f"拉取 {year}年{month}月 ...", end=" ")
        records = fetch_month(year, month, limit=1500)
        print(f"拿到 {len(records)} 条")
        all_records.extend(records)

    if not all_records:
        print("一条都没拿到，试试改年份（比如 2024、2023）")
        exit()

    df = pd.json_normalize(all_records)
    df = df.dropna(subset=["species"])

    keep_cols = [
        "species", "genus", "family", "order",
        "year", "month", "day",
        "decimalLatitude", "decimalLongitude",
        "locality", "county",
        "individualCount", "basisOfRecord",
        "datasetName", "institutionCode",
    ]
    exist_cols = [c for c in keep_cols if c in df.columns]
    df = df[exist_cols]

    df.to_csv("shenzhen_birds.csv", index=False, encoding="utf-8-sig")
    print(f"\n已保存 {len(df)} 条有效记录")

    # 展示分布
    dist = df.groupby(["year", "month"]).size()
    print("\n时间分布：")
    for (y, m), c in dist.items():
        print(f"  {int(y)}年{int(m)}月: {c}条")
    print(f"  物种总数: {df['species'].nunique()}")
