# 深圳鸟类观测数据分析 Shenzhen Bird Observation Analysis

基于 GBIF 和 iNaturalist 开放数据，分析深圳鸟类分布规律，提供交互式 Web 应用。

## 项目结构

| File | 说明 |
|------|------|
| `app.py` | **Streamlit Web 应用**（6 个功能页：总览/查询/热点/季节/百科/记录） |
| `fetch_birds.py` | 从 GBIF API 拉取深圳鸟类数据（按月份分批） |
| `fetch_inaturalist.py` | 从 iNaturalist API 拉取补充数据 |
| `search_bird.py` | 命令行鸟类查询工具 + 中英文词典（150种）+ 坐标转地名 |
| `analyze_birds.py` | 数据分析脚本（中英双语图表） |
| `bird_wiki.py` | 鸟类科普知识库（本地版，含别名/特征/习性/生境/保护/观测建议） |
| `shenzhen_birds.csv` | 主数据集（GBIF + iNaturalist 合并） |
| `images/` | 分析图表 |

## 数据集

| 指标 | 数值 |
|------|------|
| 总记录数 | 8,257 |
| 物种数 | 362 |
| 科数 | 62+ |
| 数据来源 | GBIF + iNaturalist |
| 时间范围 | 2025 全年（12 个月均衡覆盖） |

## 启动 Web 应用

```bash
pip install streamlit pandas plotly requests
streamlit run app.py
```

侧边栏 6 个功能页：

```
🏠 总览         → 统计卡片、Top 20、月度趋势、热点排名
🔍 鸟类查询     → 搜索鸟种，地图展示分布 + 地名分组统计
🗺️ 观鸟热点     → 40+ 深圳观鸟点地图，展开看各点鸟类清单
📅 季节探索     → 按季节筛选，动态图表 + 数据对比（12 个月全）
📖 鸟类百科     → 搜索鸟类，查看科普知识和深圳分布记录
📝 我的记录     → 个人观鸟日志，支持 CSV 导出
```

## 技术栈

Python, Streamlit, Pandas, Plotly, REST API (GBIF / iNaturalist)

## 数据来源

- **GBIF** (Global Biodiversity Information Facility): [gbif.org](https://www.gbif.org)
- **iNaturalist**: [inaturalist.org](https://www.inaturalist.org)
- 深圳区域：22.45-22.87°N, 113.75-114.65°E
