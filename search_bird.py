"""
鸟类查询工具 —— 输入鸟名，查找它在深圳最常出现的位置
支持中文名/学名/拼音首字母搜索，结果按地点名称分组
"""
import pandas as pd

# ========== 拼音首字母支持 ==========
try:
    from pypinyin import lazy_pinyin
    HAS_PINYIN = True
except ImportError:
    HAS_PINYIN = False

def get_py_initials(text):
    """取中文的拼音首字母，如 '白鹭' → 'bl'"""
    if not HAS_PINYIN:
        return ""
    try:
        return "".join([w[0] for w in lazy_pinyin(text)]).lower()
    except:
        return ""

# ========== 鸟类中英文词典（150种） ==========
BIRD_NAMES = {
    "Himantopus himantopus": "黑翅长脚鹬", "Ardeola bacchus": "池鹭",
    "Saxicola stejnegeri": "东亚石䳭", "Spatula clypeata": "琵嘴鸭",
    "Recurvirostra avosetta": "反嘴鹬", "Ardea cinerea": "苍鹭",
    "Egretta garzetta": "白鹭", "Milvus migrans": "黑鸢",
    "Mareca penelope": "赤颈鸭", "Phalacrocorax carbo": "普通鸬鹚",
    "Ardea alba": "大白鹭", "Tringa glareola": "林鹬",
    "Tringa nebularia": "青脚鹬", "Pycnonotus jocosus": "红耳鹎",
    "Copsychus saularis": "鹊鸲", "Motacilla tschutschensis": "东方黄鹡鸰",
    "Platalea minor": "黑脸琵鹭", "Prinia inornata": "纯色山鹪莺",
    "Garrulax perspicillatus": "黑脸噪鹛", "Lonchura punctulata": "斑文鸟",
    "Gallinula chloropus": "黑水鸡", "Anas crecca": "绿翅鸭",
    "Motacilla alba": "白鹡鸰", "Anas acuta": "针尾鸭",
    "Corvus torquatus": "白颈鸦", "Anthus hodgsoni": "树鹨",
    "Gracupica nigricollis": "黑领椋鸟", "Halcyon smyrnensis": "白胸翡翠",
    "Aythya fuligula": "凤头潜鸭", "Actitis hypoleucos": "矶鹬",
    "Amaurornis phoenicurus": "白胸苦恶鸟", "Chroicocephalus ridibundus": "红嘴鸥",
    "Pycnonotus sinensis": "白头鹎", "Tachybaptus ruficollis": "小䴙䴘",
    "Alcedo atthis": "普通翠鸟", "Lanius schach": "棕背伯劳",
    "Spilopelia chinensis": "珠颈斑鸠", "Acridotheres cristatellus": "八哥",
    "Dicrurus macrocercus": "黑卷尾", "Phoenicurus auroreus": "北红尾鸲",
    "Tringa totanus": "红脚鹬", "Orthotomus sutorius": "长尾缝叶莺",
    "Zosterops simplex": "暗绿绣眼鸟", "Gallinago gallinago": "扇尾沙锥",
    "Anthus cervinus": "红喉鹨", "Ceryle rudis": "斑鱼狗",
    "Pycnonotus aurigaster": "白喉红臀鹎", "Tringa stagnatilis": "泽鹬",
    "Numenius arquata": "白腰杓鹬", "Passer montanus": "麻雀",
    "Pluvialis squatarola": "灰斑鸻", "Vanellus vanellus": "凤头麦鸡",
    "Urocissa erythroryncha": "红嘴蓝鹊", "Acridotheres tristis": "家八哥",
    "Buteo japonicus": "普通鵟", "Parus cinereus": "大山雀",
    "Streptopelia decaocto": "灰斑鸠", "Aethopyga christinae": "叉尾太阳鸟",
    "Pandion haliaetus": "鹗", "Phylloscopus fuscatus": "褐柳莺",
    "Emberiza pusilla": "小鹀", "Spatula querquedula": "白眉鸭",
    "Turdus mandarinus": "乌鸫", "Pica serica": "喜鹊",
    "Eudynamys scolopaceus": "噪鹃", "Tringa ochropus": "白腰草鹬",
    "Centropus sinensis": "褐翅鸦鹃", "Motacilla cinerea": "灰鹡鸰",
    "Pluvialis fulva": "金斑鸻", "Ciconia boyciana": "东方白鹳",
    "Nycticorax nycticorax": "夜鹭", "Rostratula benghalensis": "彩鹬",
    "Platalea leucorodia": "白琵鹭", "Egretta intermedia": "中白鹭",
    "Prinia flaviventris": "黄腹山鹪莺", "Pericrocotus speciosus": "赤红山椒鸟",
    "Hirundo rustica": "家燕", "Myophonus caeruleus": "紫啸鸫",
    "Glareola maldivarum": "普通燕鸻", "Chloropsis hardwickii": "橙腹叶鹎",
    "Tringa erythropus": "鹤鹬", "Ardea purpurea": "草鹭",
    "Columba livia": "原鸽", "Corvus macrorhynchos": "大嘴乌鸦",
    "Rallus indicus": "普通秧鸡", "Aythya baeri": "青头潜鸭",
    "Spodiopsar sericeus": "丝光椋鸟", "Circus spilonotus": "白腹鹞",
    "Spilornis cheela": "蛇雕", "Psittacula eupatria": "亚历山大鹦鹉",
    "Aquila heliaca": "白肩雕", "Cyanopica cyanus": "灰喜鹊",
    "Streptopelia orientalis": "山斑鸠", "Numenius phaeopus": "中杓鹬",
    "Acridotheres grandis": "林八哥", "Monticola solitarius": "蓝矶鸫",
    "Hemixos castanonotus": "栗背短脚鹎", "Limosa limosa": "黑尾塍鹬",
    "Podiceps cristatus": "凤头䴙䴘", "Anas platyrhynchos": "绿头鸭",
    "Vanellus cinereus": "灰头麦鸡", "Anthus richardi": "田鹨",
    "Phylloscopus inornatus": "黄眉柳莺", "Merops philippinus": "栗喉蜂虎",
    "Aythya nyroca": "白眼潜鸭", "Anas zonorhyncha": "斑嘴鸭",
    "Picumnus innominatus": "斑姬啄木鸟", "Chroicocephalus saundersi": "黑嘴鸥",
    "Cisticola juncidis": "棕扇尾莺", "Sturnia sinensis": "灰背椋鸟",
    "Emberiza fucata": "栗耳鹀", "Numenius madagascariensis": "大杓鹬",
    "Ixos mcclellandii": "绿翅短脚鹎", "Falco tinnunculus": "红隼",
    "Dicaeum cruentatum": "朱背啄花鸟", "Phylloscopus proregulus": "黄腰柳莺",
    "Pericrocotus solaris": "灰喉山椒鸟", "Aquila clanga": "乌雕",
    "Muscicapa latirostris": "北灰鹟", "Mareca falcata": "罗纹鸭",
    "Hypsipetes leucocephalus": "黑短脚鹎", "Emberiza spodocephala": "灰头鹀",
    "Parus minor": "大山雀", "Luscinia svecica": "蓝喉歌鸲",
    "Larvivora sibilans": "红尾歌鸲", "Dicrurus hottentottus": "发冠卷尾",
    "Halcyon pileata": "蓝翡翠", "Spodiopsar cineraceus": "灰椋鸟",
    "Larus fuscus": "灰背鸥", "Ardea modesta": "大白鹭",
    "Falco peregrinus": "游隼", "Garrulax chinensis": "黑喉噪鹛",
    "Apus nipalensis": "小白腰雨燕", "Lonchura striata": "白腰文鸟",
    "Cyornis whitei": "山蓝仙鹟", "Psilopogon virens": "大拟啄木鸟",
    "Scolopax rusticola": "丘鹬", "Dicrurus leucophaeus": "灰卷尾",
    "Coracina melaschistos": "暗灰鹃鵙", "Lanius cristatus": "红尾伯劳",
    "Erpornis zantholeuca": "白腹凤鹛", "Sitta frontalis": "绒额鳾",
    "Calidris ferruginea": "弯嘴滨鹬", "Gallicrex cinerea": "董鸡",
    "Dicaeum ignipectus": "红胸啄花鸟", "Eumyias thalassinus": "铜蓝鹟",
    "Haliastur indus": "栗鸢", "Treron curvirostra": "厚嘴绿鸠",
    "Cecropis daurica": "金腰燕", "Chloris sinica": "金翅雀",
    "Falco subbuteo": "燕隼", "Motacilla flava": "黄鹡鸰",
    "Butorides striata": "绿鹭", "Ixobrychus sinensis": "黄苇鳽",
    "Bubulcus ibis": "牛背鹭", "Dendrocopos major": "大斑啄木鸟",
}


# ========== 拼音首字母 + 全拼缓存 ==========
PINYIN_INITIALS = {}   # "白鹭" → "bl"
PINYIN_FULL = {}       # "白鹭" → "bailu"
if HAS_PINYIN:
    for sp, cn in BIRD_NAMES.items():
        py = lazy_pinyin(cn)
        initials = "".join([w[0] for w in py]).lower()
        full = "".join(py).lower().replace(" ", "")
        PINYIN_INITIALS[cn] = initials
        PINYIN_INITIALS[sp] = initials
        PINYIN_FULL[cn] = full
        PINYIN_FULL[sp] = full


def match_by_pinyin(keyword):
    """拼音匹配：输入 'bl' 或 'bailu' 找到 '白鹭'"""
    if not HAS_PINYIN or not keyword:
        return []
    keyword = keyword.lower().replace(" ", "")
    results = []
    for sp, cn in BIRD_NAMES.items():
        initials = PINYIN_INITIALS.get(cn, "")
        full = PINYIN_FULL.get(cn, "")
        if (initials and initials.startswith(keyword)) or (full and full.startswith(keyword)):
            results.append(sp)
    return results


def get_cn(species):
    return BIRD_NAMES.get(species, species)


def get_label(species):
    cn = BIRD_NAMES.get(species, "")
    return f"{cn} ({species})" if cn else species


# ========== 深圳观鸟热点坐标 → 地名 ==========
HOTSPOTS = {
    (22.51, 113.96): "深圳湾公园",
    (22.48, 113.94): "福田红树林生态公园",
    (22.50, 113.93): "大沙河公园",
    (22.49, 113.95): "华侨城湿地",
    (22.48, 114.00): "红树林海滨公园",
    (22.50, 114.06): "莲花山公园",
    (22.53, 113.99): "中山公园",
    (22.53, 114.05): "福田中心区",
    (22.58, 114.26): "梧桐山",
    (22.57, 114.30): "仙湖植物园",
    (22.52, 114.11): "塘朗山",
    (22.55, 114.13): "梅林水库",
    (22.55, 114.47): "排牙山",
    (22.54, 114.52): "七娘山",
    (22.53, 114.48): "大鹏半岛",
    (22.60, 114.48): "大鹏所城",
    (22.63, 114.28): "马峦山",
    (22.69, 114.44): "葵涌",
    (22.80, 114.55): "坝光",
    (22.61, 113.83): "西湾红树林",
    (22.72, 114.02): "观澜河",
    (22.83, 114.14): "坪山河",
    (22.57, 114.17): "深圳水库",
    (22.59, 114.20): "东湖公园",
    (22.46, 114.04): "笔架山",
    (22.47, 114.06): "中心公园",
    (22.59, 113.89): "宝安公园",
    (22.45, 113.99): "小南山",
    (22.64, 113.97): "光明农场",
    (22.65, 114.35): "金沙湾",
    (22.50, 114.02): "荔枝公园",
    (22.47, 114.01): "皇岗公园",
    (22.49, 114.04): "笔架山公园",
    (22.46, 113.99): "新洲河",
    (22.51, 114.00): "市民中心",
    (22.46, 114.05): "中心公园南区",
    (22.47, 114.03): "福田口岸",
    (22.47, 114.07): "罗湖口岸",
    (22.46, 114.03): "落马洲",
    (22.56, 114.10): "银湖山",
    (22.62, 114.06): "阳台山",
    (22.78, 114.05): "松山湖（东莞）",
    (22.56, 113.93): "前海",
    (22.73, 114.08): "观澜湖",
}


def coord_to_desc(lat, lon):
    """把坐标匹配到最近的已知观鸟点"""
    nearest = min(HOTSPOTS.items(),
                  key=lambda x: ((x[0][0]-lat)**2 + (x[0][1]-lon)**2))
    dist = ((nearest[0][0]-lat)**2 + (nearest[0][1]-lon)**2) ** 0.5
    if dist < 0.08:  # 8km以内算匹配
        return nearest[1]
    return f"深圳其他区域 ({lat:.2f}, {lon:.2f})"


# ========== 读数据 ==========
df = pd.read_csv("shenzhen_birds.csv")
df["cn_name"] = df["species"].map(get_cn)


def search_bird(keyword):
    """搜索鸟类并显示按地点名称分组的结果"""
    keyword = keyword.strip().lower()

    # === 匹配物种 ===
    exact_cn = [s for s, cn in BIRD_NAMES.items() if cn == keyword]
    exact_en = [s for s in BIRD_NAMES.keys() if keyword in s.lower()]

    if exact_cn:
        candidates = exact_cn
    elif exact_en:
        candidates = exact_en
    else:
        fuzzy_cn = [s for s, cn in BIRD_NAMES.items() if keyword in cn]
        fuzzy_en = [s for s in BIRD_NAMES.keys() if keyword in s.lower()]
        # 拼音匹配（输入 "bl" 找到 "白鹭"）
        fuzzy_py = match_by_pinyin(keyword)
        candidates = list(set(fuzzy_cn + fuzzy_en + fuzzy_py))

    if not candidates:
        print(f"没有找到 [{keyword}]，试试其他关键词")
        return

    if len(candidates) > 5:
        print(f"找到多个候选：")
        for s in candidates:
            print(f"  {get_label(s)}")
        print("请用更精确的关键词再搜")
        return

    for species in candidates:
        print(f"\n{'='*55}")
        print(f"  {get_label(species)}")
        print(f"{'='*55}")

        sub = df[df["species"] == species]
        print(f"  总记录数: {len(sub)}")
        print(f"  记录月份: {sorted(sub['month'].dropna().unique())}")

        # === 按地点名称分组（核心修改） ===
        sub["location_name"] = sub.apply(
            lambda r: coord_to_desc(r["decimalLatitude"], r["decimalLongitude"]),
            axis=1
        )
        location_counts = sub["location_name"].value_counts()

        print(f"\n  主要出现位置 Top 10:")
        for i, (loc, count) in enumerate(location_counts.head(10).items(), 1):
            print(f"  {i}. {loc} — {count} 次记录")

        # 画分布图
        plot_location_distribution(species, location_counts)


def plot_location_distribution(species, location_counts):
    """画该鸟种的地点名分布条形图"""
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    cn_name = get_cn(species)
    top = location_counts.head(12)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.YlOrRd(top.values / top.values.max())
    bars = ax.barh(top.index[::-1], top.values[::-1], color=colors[::-1])
    ax.set_title(f"{cn_name} ({species})\n在深圳的主要出现位置", fontsize=13)
    ax.set_xlabel("记录次数")
    # 在条形上标数字
    for bar, val in zip(bars, top.values[::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(val), va="center", fontsize=9)
    plt.tight_layout()
    safe_name = species.replace(" ", "_")
    plt.savefig(f"images/{safe_name}_distribution.png", dpi=200)
    plt.close()
    print(f"  [图] 已保存到 images/{safe_name}_distribution.png")


# ========== 命令行交互 ==========
if __name__ == "__main__":
    print("=" * 55)
    print("  深圳鸟类位置查询工具 v2")
    print("  输入鸟名（中文/学名），查看它在深圳最常出现的位置")
    print("  结果已按地点名称分组")
    print("  输入 q 退出")
    print("=" * 55)

    while True:
        keyword = input("\n请输入鸟名 > ").strip()
        if keyword.lower() in ("q", "quit", "exit"):
            print("拜拜~")
            break
        if not keyword:
            continue
        search_bird(keyword)
