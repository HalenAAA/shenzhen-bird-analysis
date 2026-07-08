"""
从 iNaturalist 拉取深圳鸟类观测数据
补充 GBIF 覆盖不到的月份
"""
import requests
import pandas as pd
import time
import os

LAT_MIN, LAT_MAX = 22.45, 22.87
LON_MIN, LON_MAX = 113.75, 114.65
# iNaturalist 鸟类分类 ID
TAXON_ID_BIRDS = 3

PROXIES = {}
if os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY"):
    PROXIES = {"http": os.environ.get("HTTP_PROXY", ""), "https": os.environ.get("HTTPS_PROXY", "")}


def fetch_inaturalist_page(page=1, per_page=200, month=None):
    """拉取一页 iNaturalist 数据"""
    params = {
        "taxon_id": TAXON_ID_BIRDS,
        "swlat": LAT_MIN,
        "swlng": LON_MIN,
        "nelat": LAT_MAX,
        "nelng": LON_MAX,
        "page": page,
        "per_page": per_page,
        "quality_grade": "research",  # 只取研究级数据
    }
    if month:
        params["month"] = month
    try:
        resp = requests.get(
            "https://api.inaturalist.org/v1/observations",
            params=params, timeout=30, proxies=PROXIES
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [ERR] {e}")
        return None


def fetch_inaturalist(per_month=500):
    """按月拉取 iNaturalist 数据"""
    all_records = []

    for month in range(1, 13):
        page = 1
        month_count = 0
        while month_count < per_month:
            data = fetch_inaturalist_page(page=page, month=month)
            if not data or not data.get("results"):
                break
            results = data["results"]
            if not results:
                break

            for obs in results:
                taxon = obs.get("taxon") or {}
                if taxon.get("rank") != "species":
                    continue

                loc = obs.get("location", "")
                if not loc:
                    continue
                lat, lon = loc.split(",")

                # 时间解析
                observed_on = obs.get("observed_on_string", "")
                year, mo, day = 0, month, 0
                if observed_on:
                    try:
                        parts = observed_on.split(" ")[0].split("-")
                        if len(parts) == 3:
                            year = int(parts[0])
                            day = int(parts[2])
                    except:
                        pass

                all_records.append({
                    "species": taxon.get("name", ""),
                    "year": year,
                    "month": int(mo),
                    "day": day,
                    "decimalLatitude": float(lat),
                    "decimalLongitude": float(lon),
                    "locality": obs.get("place_guess", ""),
                    "quality_grade": obs.get("quality_grade", ""),
                    "source": "iNaturalist",
                    "photo_url": (taxon.get("default_photo") or {}).get("medium_url", ""),
                })
                month_count += 1

            total_pages = data.get("total_pages", 1)
            if page >= total_pages:
                break
            page += 1
            time.sleep(0.3)

        print(f"  {month}月: 拿到 {month_count} 条")
        if month_count == 0:
            print(f"   (之后月份可能没数据，停止)")
            break

    return all_records


if __name__ == "__main__":
    print("从 iNaturalist 拉取深圳鸟类数据...")
    records = fetch_inaturalist(per_month=500)

    if not records:
        print("没拿到数据，可能是网络问题")
        exit()

    df = pd.json_normalize(records)
    df = df.dropna(subset=["species"])

    df.to_csv("shenzhen_birds_inaturalist.csv", index=False, encoding="utf-8-sig")
    print(f"\n已保存 {len(df)} 条记录")

    # 打印月份分布
    dist = df.groupby("month").size()
    print("\n月份分布：")
    for m, c in dist.items():
        print(f"  {int(m)}月: {c}条")

    # 合并到主数据集
    if os.path.exists("shenzhen_birds.csv"):
        main_df = pd.read_csv("shenzhen_birds.csv")
        combined = pd.concat([main_df, df], ignore_index=True)
        combined.to_csv("shenzhen_birds.csv", index=False, encoding="utf-8-sig")
        print(f"\n已合并到主数据集: {len(combined)} 条")
