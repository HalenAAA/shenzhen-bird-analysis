"""
深圳鸟类观测数据拉取
基于 GBIF (Global Biodiversity Information Facility) API
"""
import requests
import pandas as pd
import time
import os

# 深圳的经纬度范围
LAT_MIN, LAT_MAX = 22.45, 22.87
LON_MIN, LON_MAX = 113.75, 114.65

# 鸟类在 GBIF 的分类编号
TAXON_KEY_AVES = 212

# 如果 GBIF 连不上，试试走代理（比如 Clash/v2ray 默认端口）
PROXIES = {}
if os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY"):
    PROXIES = {
        "http": os.environ.get("HTTP_PROXY", ""),
        "https": os.environ.get("HTTPS_PROXY", ""),
    }

def fetch_birds(limit=5000):
    """从 GBIF 拉取深圳鸟类观测记录"""
    all_records = []
    offset = 0
    url = "https://api.gbif.org/v1/occurrence/search"

    while offset < limit:
        params = {
            "taxonKey": TAXON_KEY_AVES,
            "decimalLatitude": f"{LAT_MIN},{LAT_MAX}",
            "decimalLongitude": f"{LON_MIN},{LON_MAX}",
            "limit": 300,
            "offset": offset,
        }
        try:
            resp = requests.get(
                url, params=params, timeout=60, proxies=PROXIES
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
            all_records.extend(results)
            offset += len(results)
            print(f"[OK] 已获取 {len(all_records)} 条记录...")
            time.sleep(0.5)
        except requests.exceptions.ConnectTimeout:
            print("[FAIL] 连接超时，可能是网络问题")
            print("尝试方法：")
            print("  1. 如果你在用代理（Clash/v2ray/SS），先设置环境变量再跑：")
            print("     set HTTP_PROXY=http://127.0.0.1:7890")
            print("     set HTTPS_PROXY=http://127.0.0.1:7890")
            print("     py fetch_birds.py")
            print("  2. 或者直接打开 https://api.gbif.org 看看能不能访问")
            break
        except Exception as e:
            print(f"[FAIL] 请求出错: {e}")
            break

    print(f"\n[Done] 共获取 {len(all_records)} 条深圳鸟类观测记录")
    return all_records


if __name__ == "__main__":
    records = fetch_birds(limit=5000)

    if not records:
        print("\n直接下载不行，试试从浏览器手动下载：")
        print("1. 打开 https://www.gbif.org/occurrence/search")
        print("2. 筛选条件：Taxon = Aves, 地图拖到深圳区域")
        print("3. 点 Download -> CSV")
        print("4. 下载后放到本目录，改名叫 shenzhen_birds.csv")
        exit()

    # 展平嵌套的 JSON，存成 CSV
    df = pd.json_normalize(records)

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

    # 只保留有物种鉴定的记录
    df = df.dropna(subset=["species"])

    df.to_csv("shenzhen_birds.csv", index=False, encoding="utf-8-sig")
    print(f"[Save] 已保存到 shenzhen_birds.csv，共 {len(df)} 条有效记录")
