import streamlit as st
import random
import time

# ================= 配置网页 =================
st.set_page_config(
    page_title="卷卷·换号抽签器",
    page_icon="⚔️",
    layout="centered"
)

# ================= 1. 数据中心 (在这里修改号池) =================
# 格式： "心法名": ["账号A", "账号B"]
ACCOUNT_POOL = {
    "紫霞功(气纯)": ["道长01", "备胎气纯"],
    "太虚剑意(剑纯)": [],
    "冰心诀": ["秀姐A"],
    "离经易道(奶花)": ["花哥", "花萝"],
    "易筋经(和尚)": ["大师"],
    "铁牢律(T)": ["天策T"],
    # ... 你可以在这里继续添加，没写的默认是空列表
}

# 剑三全门派数据
JX3_DATA = {
    "纯阳": [{"n": "紫霞功(气纯)", "r": "D"}, {"n": "太虚剑意(剑纯)", "r": "D"}],
    "万花": [{"n": "花间游", "r": "D"}, {"n": "离经易道(奶花)", "r": "奶"}],
    "少林": [{"n": "易筋经(和尚)", "r": "D"}, {"n": "洗髓经(T)", "r": "T"}],
    "七秀": [{"n": "冰心诀", "r": "D"}, {"n": "云裳心经(奶秀)", "r": "奶"}],
    "天策": [{"n": "傲血战意", "r": "D"}, {"n": "铁牢律(T)", "r": "T"}],
    "藏剑": [{"n": "问水/山居(藏剑)", "r": "D"}],
    "五毒": [{"n": "毒经", "r": "D"}, {"n": "补天诀(奶毒)", "r": "奶"}],
    "唐门": [{"n": "惊羽诀", "r": "D"}, {"n": "天罗诡道(田螺)", "r": "D"}],
    "明教": [{"n": "焚影圣诀", "r": "D"}, {"n": "明尊琉璃体(T)", "r": "T"}],
    "丐帮": [{"n": "笑尘诀", "r": "D"}],
    "苍云": [{"n": "分山劲", "r": "D"}, {"n": "铁骨衣(T)", "r": "T"}],
    "长歌": [{"n": "莫问", "r": "D"}, {"n": "相知(奶歌)", "r": "奶"}],
    "霸刀": [{"n": "北傲诀", "r": "D"}],
    "蓬莱": [{"n": "凌海诀", "r": "D"}],
    "凌雪": [{"n": "隐龙诀", "r": "D"}],
    "衍天": [{"n": "太玄经", "r": "D"}],
    "药宗": [{"n": "无方", "r": "D"}, {"n": "灵素(奶药)", "r": "奶"}],
    "刀宗": [{"n": "孤锋诀", "r": "D"}],
    "万灵": [{"n": "山海心诀", "r": "D"}],
    "流派": [{"n": "无相楼", "r": "D"}],
    "段氏": [{"n": "周天诀", "r": "D"}]
}

# ================= 2. 样式美化 (CSS) =================
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #c8a063;
        color: white;
        font-weight: bold;
    }
    .result-box {
        padding: 20px;
        background-color: #fdf6e3;
        border-left: 5px solid #d32f2f;
        border-radius: 5px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 20px;
    }
    .highlight { color: #d32f2f; }
</style>
""", unsafe_allow_html=True)

# ================= 3. 逻辑控制 =================

# 初始化 Session State (用于记录状态)
if 'agreed' not in st.session_state:
    st.session_state.agreed = False
if 'result' not in st.session_state:
    st.session_state.result = None

# --- 界面：军令状 ---
if not st.session_state.agreed:
    st.title("📜 换号副本 · 军令状")
    st.info("请全员阅读并确认规则：")
    st.markdown("""
    1. **坦诚相待**：绝不隐瞒所会心法，拒绝伪装萌新。
    2. **号人合一**：确认参战后，人号必须同时到位。
    3. **硬核手打**：全程 **禁用宏、武学助手**，坚持手打至通关。
    """)
    if st.button("我同意并画押"):
        st.session_state.agreed = True
        st.rerun()

# --- 界面：主抽签区 ---
else:
    st.title("🗡️ 卷卷 · 换号抽签器")
    
    # 1. 输入ID
    player_id = st.text_input("请输入你的游戏ID", placeholder="例如：卷卷")

    # 2. 侧边栏：设置与号池查看
    with st.sidebar:
        st.header("⚙️ 设置与号池")
        only_account_mode = st.toggle("🔒 只抽有号模式", value=True, help="开启后，没有录入账号的心法不会被抽中")
        
        st.divider()
        st.subheader("📊 当前号池公示")
        # 遍历显示有号的心法
        has_account_count = 0
        for xf, accs in ACCOUNT_POOL.items():
            if accs:
                st.write(f"**{xf}**: {', '.join(accs)}")
                has_account_count += 1
        if has_account_count == 0:
            st.warning("当前号池为空！请联系管理员(卷卷)在后台添加账号。")

    # 3. 排除选项 (使用多选框)
    st.subheader("👇 排除你会玩的/不想抽的")
    
    # 提取所有心法列表
    all_xinfas = []
    for sect, xfs in JX3_DATA.items():
        for x in xfs:
            all_xinfas.append(x)
            
    # 快捷筛选辅助
    col1, col2, col3 = st.columns(3)
    filter_role = None
    if col1.button("排除所有 T"): filter_role = "T"
    if col2.button("排除所有 奶"): filter_role = "奶"
    if col3.button("重置选项"): filter_role = "RESET"

    # 处理 Session State 中的排除列表
    if 'excluded' not in st.session_state or filter_role == "RESET":
        st.session_state.excluded = []
    
    if filter_role and filter_role != "RESET":
        to_add = [x['n'] for x in all_xinfas if x['r'] == filter_role]
        st.session_state.excluded = list(set(st.session_state.excluded + to_add))

    # 显示多选框
    excluded_options = st.multiselect(
        "选择要排除的心法:",
        options=[x['n'] for x in all_xinfas],
        default=st.session_state.excluded,
        key='excluded_widget' # 绑定key以便同步
    )
    # 同步回 session state
    st.session_state.excluded = excluded_options

    # 4. 抽签按钮逻辑
    if st.button("🔥 开始抽签", type="primary"):
        if not player_id:
            st.error("请先输入游戏ID！")
        else:
            # === 核心算法 ===
            valid_candidates = []
            
            for xf in all_xinfas:
                xf_name = xf['n']
                
                # 1. 如果被排除了，跳过
                if xf_name in excluded_options:
                    continue
                
                # 2. 如果开启了只抽有号模式
                if only_account_mode:
                    accounts = ACCOUNT_POOL.get(xf_name, [])
                    if not accounts:
                        continue # 没号跳过
                
                valid_candidates.append(xf_name)
            
            # === 结果判断 ===
            if not valid_candidates:
                st.error("没有符合条件的心法！(可能是全都排除了，或者号池里没有剩余可选的)")
            else:
                # 动画效果
                with st.spinner('天命轮转中...'):
                    time.sleep(1) # 假装思考1秒
                
                # 抽心法
                final_xinfa = random.choice(valid_candidates)
                
                # 抽账号
                final_account = ""
                accounts_in_pool = ACCOUNT_POOL.get(final_xinfa, [])
                if accounts_in_pool:
                    final_account = random.choice(accounts_in_pool)
                
                # 生成结果文本
                if final_account:
                    res_str = f"使用 【{final_xinfa}】\n账号：{final_account}"
                else:
                    res_str = f"使用 【{final_xinfa}】\n(需自行找号)"
                
                st.session_state.result = {
                    "id": player_id,
                    "text": res_str
                }

    # 5. 显示结果
    if st.session_state.result:
        res = st.session_state.result
        st.markdown(f"""
        <div class="result-box">
            📝 判决书<br>
            侠士 <span class="highlight">{res['id']}</span><br>
            {res['text'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("重置"):
            st.session_state.result = None
            st.rerun()
