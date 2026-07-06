# 深圳鸟类观测数据分析 Shenzhen Bird Observation Analysis

基于 GBIF 开放数据分析深圳鸟类分布规律。

## 项目结构

| File | Description |
|------|-------------|
| `fetch_birds.py` | 从 GBIF API 拉取深圳鸟类观测数据 |
| `analyze_birds.py` | 数据清洗 + 可视化分析（中英双语图表） |
| `search_bird.py` | **鸟类位置查询工具** — 输入鸟名，查找深圳最频出现地点 |
| `shenzhen_birds.csv` | 数据集（5001 条记录） |
| `images/` | 分析结果图表 |

## 快速使用

```bash
pip install pandas matplotlib seaborn requests

python fetch_birds.py           # 拉取数据（已有可跳过）
python analyze_birds.py         # 生成分析图表
python search_bird.py           # 启动鸟类查询工具
```

## 分析结果

| 指标 | 数值 |
|------|------|
| 总记录数 | 5,001 |
| 物种数 | 232 |
| 科数 | 59 |
| 数据年份 | 2026 |

### 深圳观测最多的鸟类 Top 5

| 中文名 | 学名 | 记录数 |
|--------|------|-------|
| 黑翅长脚鹬 | Himantopus himantopus | 161 |
| 池鹭 | Ardeola bacchus | 151 |
| 东亚石䳭 | Saxicola stejnegeri | 138 |
| 琵嘴鸭 | Spatula clypeata | 135 |
| 反嘴鹬 | Recurvirostra avosetta | 130 |

## 鸟类查询功能

`search_bird.py` 支持按中文名或学名搜索，查看某物种在深圳的主要出现位置：

```
请输入鸟名 > 黑脸琵鹭
请输入鸟名 > egret
请输入鸟名 > platalea
```

结果已按地点名称分组展示，并自动生成分布图。

## 数据来源

GBIF (Global Biodiversity Information Facility) — 深圳区域（22.45-22.87°N, 113.75-114.65°E）鸟类观测记录。
