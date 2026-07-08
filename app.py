"""
深圳鸟类观察分析 —— Streamlit Web 应用 v2
功能：总览 / 鸟类查询 / 观鸟热点 / 季节探索 / 鸟类百科 / 我的记录
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from search_bird import BIRD_NAMES, HOTSPOTS, coord_to_desc, get_cn, get_label
from bird_wiki import get_local_fact, get_en_name, get_inaturalist_photo_url
import pandas as pd

st.set_page_config(page_title="深圳鸟类观察分析", layout="wide", page_icon="🐦")

# ===== 加载数据 =====
@st.cache_data
def load_data():
    df = pd.read_csv("shenzhen_birds.csv")
    df["cn_name"] = df["species"].map(get_cn)
    df["location_name"] = df.apply(
        lambda r: coord_to_desc(r["decimalLatitude"], r["decimalLongitude"]),
        axis=1
    )
    df["data_source"] = df["source"].fillna("GBIF") if "source" in df.columns else "GBIF"
    return df

df = load_data()

# ===== 侧边栏 =====
st.sidebar.title("🐦 深圳鸟类图鉴")
st.sidebar.caption(f"数据：GBIF + iNaturalist")
st.sidebar.caption(f"{len(df):,} 条记录 · {df['species'].nunique()} 种")

page = st.sidebar.radio("导航", [
    "🏠 总览", "🔍 鸟类查询", "🗺️ 观鸟热点",
    "📅 季节探索", "📖 鸟类百科", "📝 我的记录"
])

st.sidebar.markdown("---")

# ===== 工具函数：带标签的地图（自动降级） =====
def plot_labeled_map(data, title="", height=400):
    """用 Plotly 画带中文地点名的地图，失败时降级到 st.map"""
    if data.empty:
        st.info("暂无位置数据")
        return

    map_data = data.rename(columns={
        "decimalLatitude": "lat", "decimalLongitude": "lon"
    })

    try:
        fig = px.scatter_map(
            map_data, lat="lat", lon="lon", text="location_name",
            zoom=10, height=height, title=title,
            map_style="basic",   # 简洁底图，英文标注少，我们自己的中文标签更突出
        )
        fig.update_traces(
            marker={"size": 12, "color": "#FF4444", "line": {"width": 2, "color": "white"}},
            textposition="top center",
            textfont={"size": 12, "color": "#CC0000", "family": "Arial", "weight": "bold"}
        )
        fig.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            paper_bgcolor="white",
            plot_bgcolor="white",
            font={"color": "#333333"},
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        # Plotly 地图渲染失败时降级
        st.warning("⚠️ 地图加载中，已切换为简洁模式")
        st.map(map_data[["lat", "lon"]], use_container_width=True, zoom=10)
        # 同时用表格展示地名
        loc_counts = data["location_name"].value_counts().head(8).reset_index()
        loc_counts.columns = ["地点", "次数"]
        st.dataframe(loc_counts, use_container_width=True, hide_index=True)


# ====================================================================
# 页面 1：总览
# ====================================================================
if page == "🏠 总览":
    st.title("深圳鸟类观察分析总览")
    st.caption("Shenzhen Bird Observation Overview")

    has_source = "source" in df.columns
    gbif_count = len(df[df.get("source", "") != "iNaturalist"]) if has_source else "-"
    inat_count = len(df[df.get("source", "") == "iNaturalist"]) if has_source else "-"

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("总记录数", f"{len(df):,}", "Total Records")
    with col2: st.metric("物种数", f"{df['species'].nunique():,}", "Species")
    with col3: st.metric("科数", f"{df['family'].nunique()}", "Families")
    with col4:
        top_bird = df["species"].value_counts().index[0]
        st.metric("最常见", get_label(top_bird), "Most Common")

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.subheader("深圳鸟类 Top 20")
        top20 = df["species"].value_counts().head(20)
        top20_df = pd.DataFrame({
            "物种": [get_label(s) for s in top20.index],
            "记录数": top20.values
        })
        fig = px.bar(top20_df, x="记录数", y="物种", orientation="h",
                     color="记录数", color_continuous_scale="YlOrRd")
        fig.update_layout(height=450, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("各月物种数 / Species by Month")
        # 按来源拆分，避免 GBIF 集中在4个月份造成的偏差
        if "source" in df.columns:
            monthly_source = df.groupby(["month", "data_source"]).size().reset_index(name="记录数")
            monthly_source["月份"] = monthly_source["month"].apply(lambda m: f"{int(m)}月")
            fig2 = px.bar(monthly_source, x="月份", y="记录数", color="data_source",
                          barmode="group",
                          color_discrete_map={"GBIF": "#4A90D9", "iNaturalist": "#7EC850"},
                          title="各月记录数 / Records by Month (GBIF vs iNaturalist)")
            fig2.update_layout(legend={"title": "来源", "orientation": "h", "y": 1.1})
        else:
            monthly_sp = df.groupby("month")["species"].nunique()
            mon_df = pd.DataFrame({"月份": [f"{m}月" for m in monthly_sp.index], "物种数": monthly_sp.values})
            fig2 = px.bar(mon_df, x="月份", y="物种数", text_auto=True,
                          color="物种数", color_continuous_scale="Viridis")
            fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("深圳观鸟热点总览 / Birding Hotspots")
    hotspot_summary = df.groupby("location_name").agg(
        记录数=("species", "count"),
        物种数=("species", "nunique")
    ).sort_values("记录数", ascending=False).head(20).reset_index()
    hotspot_summary.columns = ["地点", "记录数", "物种数"]
    fig3 = px.bar(hotspot_summary, x="记录数", y="地点", orientation="h",
                  color="物种数", color_continuous_scale="Tealgrn",
                  title="Top 20 Hotspots")
    fig3.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig3, use_container_width=True)

# ====================================================================
# 页面 2：鸟类查询
# ====================================================================
elif page == "🔍 鸟类查询":
    st.title("🔍 鸟类位置查询")
    st.caption("输入鸟名，查看它在深圳的主要出现位置")

    search_text = st.text_input("输入中文名或学名", placeholder="例：白鹭、egret、黑脸琵鹭")

    if search_text:
        keyword = search_text.strip().lower()
        exact_cn = [s for s, cn in BIRD_NAMES.items() if cn == keyword]
        exact_en = [s for s in BIRD_NAMES.keys() if keyword in s.lower()]

        if exact_cn:
            candidates = exact_cn
        elif exact_en:
            candidates = exact_en
        else:
            fuzzy_cn = [s for s, cn in BIRD_NAMES.items() if keyword in cn]
            fuzzy_en = [s for s in BIRD_NAMES.keys() if keyword in s.lower()]
            candidates = list(set(fuzzy_cn + fuzzy_en))

        if not candidates:
            st.warning(f"没有找到「{search_text}」")
        elif len(candidates) > 5:
            st.info(f"找到多个候选：")
            cols = st.columns(min(len(candidates), 3))
            for i, s in enumerate(candidates):
                cols[i % 3].write(f"- {get_label(s)}")
        else:
            for species in candidates:
                sub = df[df["species"] == species]
                cn_name = get_cn(species)

                st.markdown(f"### {cn_name} / {species}")

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("总记录数", len(sub))
                    months = sorted(sub["month"].dropna().unique())
                    month_str = ", ".join([f"{int(m)}月" for m in months])
                    st.write(f"📅 出现月份：{month_str}")

                    loc_counts = sub["location_name"].value_counts().head(10)
                    st.write("**📍 主要出现位置：**")
                    for i, (loc, cnt) in enumerate(loc_counts.items(), 1):
                        st.write(f"  {i}. {loc} — {cnt}次")

                with col2:
                    plot_labeled_map(sub,
                        f"{cn_name} 在深圳的分布 / Distribution")

                loc_df = sub["location_name"].value_counts().head(12).reset_index()
                loc_df.columns = ["地点", "记录数"]
                fig = px.bar(loc_df, x="记录数", y="地点", orientation="h",
                             color="记录数", color_continuous_scale="YlOrRd",
                             title=f"{cn_name} 在深圳的分布")
                fig.update_layout(height=300, yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("---")

# ====================================================================
# 页面 3：观鸟热点
# ====================================================================
elif page == "🗺️ 观鸟热点":
    st.title("🗺️ 深圳观鸟热点")
    st.caption("地图上标出了深圳的主要观鸟地点，点击展开查看各点鸟类记录")

    hotspot_data = []
    for (lat, lon), name in HOTSPOTS.items():
        nearby = df[df["location_name"] == name]
        hotspot_data.append({
            "decimalLatitude": lat,
            "decimalLongitude": lon,
            "location_name": name,
            "记录数": len(nearby),
            "物种数": nearby["species"].nunique()
        })
    hotspot_df = pd.DataFrame(hotspot_data)

    # 带标签的地图
    fig_map = px.scatter_map(
        hotspot_df, lat="decimalLatitude", lon="decimalLongitude",
        text="location_name",
        size="记录数", color="物种数",
        color_continuous_scale="Viridis",
        zoom=10, height=500,
        title="深圳观鸟热点地图 / Birding Hotspots"
    )
    fig_map.update_traces(textposition="top center", textfont={"size": 9})
    fig_map.update_layout(map={"style": "open-street-map"},
                          margin={"r": 0, "t": 30, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

    # 热点详情
    st.subheader("热点详情")
    hotspot_sorted = hotspot_df.sort_values("记录数", ascending=False)
    for _, row in hotspot_sorted.iterrows():
        with st.expander(f"{row['location_name']} — {row['物种数']} 种 · {row['记录数']} 条"):
            nearby = df[df["location_name"] == row["location_name"]]
            top10 = nearby["species"].value_counts().head(10)
            for s, cnt in top10.items():
                st.write(f"- {get_label(s)}：{cnt}次")

# ====================================================================
# 页面 4：季节探索
# ====================================================================
elif page == "📅 季节探索":
    st.title("📅 季节探索")
    st.caption("查看深圳鸟类在全年的变化——12个月全覆盖")

    # 季节选择
    SEASONS = {
        "❄️ 冬季 (12-2月)": [12, 1, 2],
        "🌱 春季 (3-5月)": [3, 4, 5],
        "☀️ 夏季 (6-8月)": [6, 7, 8],
        "🍂 秋季 (9-11月)": [9, 10, 11],
        "📅 全年": list(range(1, 13)),
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        season_choice = st.radio("选择季节", list(SEASONS.keys()))
        season_months = SEASONS[season_choice]
        season_df = df[df["month"].isin(season_months)]

        st.info(f"📊 {len(season_df):,} 条记录\n{season_df['species'].nunique()} 种鸟类")
        if "source" in season_df.columns:
            src = season_df["source"].fillna("GBIF").value_counts()
            for s, c in src.items():
                st.caption(f"{s}: {c} 条")

        # 系统推荐
        st.markdown("**🌟 推荐观鸟点：**")
        top_spots = season_df.groupby("location_name").size().sort_values(ascending=False).head(5)
        for spot, cnt in top_spots.items():
            sp_count = season_df[season_df["location_name"] == spot]["species"].nunique()
            st.write(f"- {spot}（{sp_count} 种 · {cnt} 条）")

    with col2:
        # 物种数对比
        compare_data = []
        for sname, smonths in SEASONS.items():
            if sname == "📅 全年":
                continue
            sdf = df[df["month"].isin(smonths)]
            compare_data.append({"季节": sname[:4], "物种数": sdf["species"].nunique()})
        cmp_df = pd.DataFrame(compare_data)
        colors = {"❄️": "#4A90D9", "🌱": "#7EC850", "☀️": "#F5A623", "🍂": "#D0021B"}
        fig_compare = px.bar(cmp_df, x="季节", y="物种数", text_auto=True,
                             color="季节",
                             color_discrete_map=colors,
                             title="各季节物种多样性对比")
        fig_compare.update_layout(showlegend=False)
        st.plotly_chart(fig_compare, use_container_width=True)

    # 当前季节的 Top 15
    st.subheader(f"{season_choice} 最常见鸟类 Top 15")
    top15 = season_df["species"].value_counts().head(15)
    top15_df = pd.DataFrame({
        "物种": [get_label(s) for s in top15.index],
        "记录数": top15.values
    })
    fig = px.bar(top15_df, x="记录数", y="物种", orientation="h",
                 color="记录数", color_continuous_scale="Sunsetdark",
                 title=f"Top 15 Birds in {season_choice}")
    fig.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    # 月度趋势（按来源拆分）
    monthly_source = season_df.groupby(["month", "data_source"]).size().reset_index(name="记录数")
    monthly_source["月份"] = monthly_source["month"].apply(lambda m: f"{int(m)}月")
    fig2 = px.bar(monthly_source, x="月份", y="记录数", color="data_source",
                  barmode="group",
                  color_discrete_map={"GBIF": "#4A90D9", "iNaturalist": "#7EC850"},
                  title="月度记录数趋势 / Monthly Records by Source")
    fig2.update_layout(legend={"title": "来源", "orientation": "h", "y": 1.1})
    st.plotly_chart(fig2, use_container_width=True)

    # 物种列表
    with st.expander("📋 查看该季节全部物种"):
        sl = season_df.groupby(["species", "cn_name", "family"]).size().reset_index(name="记录数")
        sl = sl.sort_values("记录数", ascending=False)
        sl.columns = ["学名", "中文名", "科", "记录数"]
        st.dataframe(sl, use_container_width=True, hide_index=True)

# ====================================================================
# 页面 5：鸟类百科
# ====================================================================
elif page == "📖 鸟类百科":
    st.title("📖 鸟类百科")
    st.caption("搜索一种鸟，查看图文介绍、生态知识和在深圳的出现规律")

    # 构建搜索选项（只含词典中的常见种）
    known_species = [(cn, sp) for sp, cn in BIRD_NAMES.items()]
    known_species.sort(key=lambda x: x[0])

    search_term = st.text_input("搜索鸟类（中文名或学名）", placeholder="例：白鹭、翠鸟、sparrow")

    if search_term:
        keyword = search_term.strip().lower()
        matches = [(cn, sp) for cn, sp in known_species if keyword in cn.lower() or keyword in sp.lower()]

        if not matches:
            st.warning(f"没有找到「{search_term}」")
        elif len(matches) > 10:
            st.info(f"找到 {len(matches)} 个结果，请输入更精确的关键词")
            for cn, sp in matches[:20]:
                st.write(f"- {cn} / {sp}")
        else:
            for cn_name, species in matches:
                sub = df[df["species"] == species]
                local_fact = get_local_fact(cn_name)
                en_name = get_en_name(species)
                img_url = get_inaturalist_photo_url(species, df)

                st.markdown(f"## {cn_name} / {species}")

                col1, col2 = st.columns([1, 1.5])

                with col1:
                    # 图片
                    if img_url:
                        st.image(img_url, use_container_width=True,
                                 caption=f"{cn_name} — 照片来自 iNaturalist（仅供参考）")
                        st.caption("💡 照片可能不准确，欢迎自行替换")
                    else:
                        st.info("📷 暂无照片")

                    # 数据指标
                    st.markdown("**📊 在深圳的记录：**")
                    st.metric("总记录数", len(sub))
                    if not sub.empty:
                        months = sorted(sub["month"].dropna().unique())
                        month_str = ", ".join([f"{int(m)}月" for m in months])
                        st.write(f"📅 出现月份：{month_str}")
                        st.write(f"📍 出现地点：{sub['location_name'].nunique()} 个")
                        if "family" in sub.columns:
                            st.write(f"🏛️ 科：{sub['family'].iloc[0]}")
                        if en_name:
                            st.write(f"🌐 英文名：{en_name}")

                with col2:
                    if local_fact:
                        st.markdown("**📚 科普知识**")
                        for key, val in local_fact.items():
                            st.markdown(f"**{key}：**{val}")
                    else:
                        st.info("暂无科普资料，欢迎贡献！")

                # 分布地图
                st.markdown("---")
                st.subheader(f"{cn_name} 在深圳的分布")
                if not sub.empty:
                    plot_labeled_map(sub, height=350)
                else:
                    st.info("该物种暂无深圳分布记录")

                st.markdown("---")

# ====================================================================
# 页面 6：我的记录
# ====================================================================
elif page == "📝 我的记录":
    st.title("📝 我的观鸟记录")
    st.caption("记录你每次观鸟的发现，建立自己的深圳观鸟日记")

    if "my_records" not in st.session_state:
        st.session_state.my_records = []

    st.subheader("✏️ 添加记录")
    col1, col2, col3 = st.columns(3)
    with col1:
        record_date = st.date_input("日期", datetime.now())
    with col2:
        loc_options = list(HOTSPOTS.values())
        record_location = st.selectbox("地点", loc_options)
    with col3:
        bird_options = [f"{cn} ({sp})" for sp, cn in BIRD_NAMES.items()]
        record_bird = st.selectbox("鸟种", bird_options)

    record_note = st.text_area("备注", placeholder="数量、行为、天气……")
    record_photo = st.text_input("照片链接（可选）", placeholder="https://...")

    if st.button("✅ 保存记录"):
        species = record_bird.split(" (")[1].rstrip(")") if " (" in record_bird else record_bird
        record = {
            "日期": record_date.strftime("%Y-%m-%d"),
            "地点": record_location,
            "鸟种": record_bird,
            "学名": species,
            "备注": record_note,
            "照片": record_photo,
            "记录时间": datetime.now().strftime("%H:%M"),
        }
        st.session_state.my_records.append(record)
        st.success("✅ 记录已保存！")

    st.subheader(f"📋 我的观鸟日记（共 {len(st.session_state.my_records)} 条）")
    if st.session_state.my_records:
        records_df = pd.DataFrame(st.session_state.my_records)
        st.dataframe(records_df[["日期", "地点", "鸟种", "备注"]],
                     use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("总记录数", len(records_df))
        with col2: st.metric("记录鸟种", records_df["学名"].nunique())
        with col3:
            top = records_df["地点"].mode().iloc[0] if not records_df.empty else "-"
            st.metric("最常去的", top)

        csv = records_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 下载 CSV", csv,
                           file_name=f"my_records_{datetime.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv")
        if st.button("🗑️ 清空"):
            st.session_state.my_records = []
            st.rerun()
    else:
        st.info("还没有记录，添加第一条吧 🐦")

    st.markdown("---")
    st.caption("💡 记录保存在当前浏览器，关闭会丢失。建议定期下载 CSV。")
