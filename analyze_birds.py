"""
深圳鸟类观测数据分析 —— 中英双语版
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
matplotlib.rcParams["axes.unicode_minus"] = False

# 从 search_bird.py 复用完整 150 种鸟类词典
from search_bird import BIRD_NAMES, get_cn as cn, get_label as label

# ========== 1. 读数据 ==========
df = pd.read_csv("shenzhen_birds.csv")
print(f"Total records: {len(df)} | 总记录数: {len(df)}")
print(f"Species: {df['species'].nunique()} | 物种数: {df['species'].nunique()}")

# ========== 2. Top 20 ==========
top20 = df["species"].value_counts().head(20)
top20_labels = [label(s) for s in top20.index]

fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh(top20_labels, top20.values, color="steelblue")
ax.set_title("Top 20 Birds in Shenzhen / 深圳观测最多的 20 种鸟类", fontsize=14)
ax.set_xlabel("Record Count / 观测次数")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig("images/top20_birds.png", dpi=200)
plt.close()

# ========== 3. 各月观测数量 ==========
monthly = df["month"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly.index, monthly.values, marker="o", color="forestgreen")
ax.set_title("Monthly Observation Pattern / 深圳鸟类观测月度分布", fontsize=14)
ax.set_xlabel("Month / 月份")
ax.set_ylabel("Record Count / 观测次数")
ax.set_xticks(range(1, 13))
month_names = ["Jan\n1月","Feb\n2月","Mar\n3月","Apr\n4月","May\n5月","Jun\n6月",
               "Jul\n7月","Aug\n8月","Sep\n9月","Oct\n10月","Nov\n11月","Dec\n12月"]
ax.set_xticklabels(month_names)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("images/monthly_pattern.png", dpi=200)
plt.close()

# ========== 4. 各科物种丰富度 ==========
family_richness = df.groupby("family")["species"].nunique().sort_values(ascending=False).head(15)

fig, ax = plt.subplots(figsize=(10, 6))
family_richness.plot(kind="bar", color="coral", ax=ax)
ax.set_title("Family Diversity Top 15 / 深圳鸟类科级多样性 Top 15", fontsize=14)
ax.set_xlabel("Family / 科")
ax.set_ylabel("Species Count / 物种数")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("images/family_diversity.png", dpi=200)
plt.close()

# ========== 5. 月份 × 物种热力图 ==========
top_species = df["species"].value_counts().head(8).index
df_top = df[df["species"].isin(top_species)]
month_species = df_top.groupby(["month", "species"]).size().unstack(fill_value=0)
month_species.columns = [label(c) for c in month_species.columns]

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(month_species, cmap="YlGnBu", ax=ax, annot=True, fmt="d")
ax.set_title("Species x Month Heatmap / 主要鸟类各月出现频次", fontsize=14)
ax.set_xlabel("Species / 物种")
ax.set_ylabel("Month / 月份")
plt.tight_layout()
plt.savefig("images/species_month_heatmap.png", dpi=200)
plt.close()

print("\n[Done] All charts saved to images/ | 所有图表已保存")

# ========== 快速统计 ==========
print(f"\n=== Quick Summary / 快速统计 ===")
print(f"Total records / 总记录数: {len(df)}")
print(f"Species / 物种总数: {df['species'].nunique()}")
print(f"Families / 科总数: {df['family'].nunique()}")
print(f"Top bird / 观测最多的鸟: {label(df['species'].value_counts().index[0])}")
