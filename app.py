import streamlit as st
import random
import pandas as pd
from datetime import datetime

# ================= 配置网页 =================
st.set_page_config(page_title="25人本·全自动发号机", page_icon="⚔️", layout="wide")

# ================= 1. 核心数据与全局状态 =================
# 这里使用了 st.cache_resource 来模拟一个“全局数据库”
# 只要服务器不重启，所有人的数据都会存在这里

@st.cache_resource
class GameState:
    def __init__(self):
        # 预设号池：格式 {"心法": ["账号A", "账号B"]}
        # 请在这里填入你所有的公用账号
        self.ACCOUNT_POOL = {
            "铁牢律(T)": ["策T-01", "策T-02", "策T-03"],
            "洗髓经(T)": ["大师T-01", "大师T-02"],
            "明尊琉璃体(T)": ["喵T-01", "喵T-02"],
            "铁骨衣(T)": ["苍云T-01"],
            
            "离经易道(奶花)": ["花奶-01", "花奶-02"],
            "云裳心经(奶秀)": ["秀奶-01", "秀奶-02"],
            "补天诀(奶毒)": ["毒奶-01", "毒奶-02"],
            "相知(奶歌)": ["歌奶-01"],
            "灵素(奶药)": ["药奶-01"],
            
            "紫霞功(气纯)": ["气纯-01", "气纯-02", "气纯-03"],
            "太虚剑意(剑纯)": ["剑纯-01"],
            "花间游": ["花间-01", "花间-02"],
            "易筋经(和尚)": ["秃秃-01"],
            "冰心诀": ["冰心-01", "冰心-02", "冰心-03"],
            "傲血战意": ["天策-01"],
            "问水/山居(藏剑)": ["藏剑-01", "藏剑-02"],
            "毒经": ["毒经-01"],
            "惊羽诀": ["鲸鱼-01"],
            "天罗诡道(田螺)": ["田螺-01", "田螺-02"],
            "焚影圣诀": ["明教-01"],
            "笑尘诀": ["丐帮-01"],
            "分山劲": ["苍云-01"],
            "莫问": ["莫问-01"],
            "北傲诀": ["霸刀-01"],
            "凌海诀": ["蓬莱-01"],
            "隐龙诀": ["凌雪-01"],
            "太玄经": ["衍天-01"],
            "无方": ["药宗-01"],
            "孤锋诀": ["刀宗-01"],
            "山海心诀": ["万灵-01"],
            "无相楼": ["流派-01"],
            "周天诀": ["段氏-01"]
        }
        
        # 目标配置
        self.TARGET_CONFIG = {"T": 2, "N": 4, "DPS": 19}
        
        # 已使用账号记录 (防止重复发号) set()
        self.used_accounts = set()
        
        # 玩家名单 (记录谁抽到了什么)
        # 格式: [{"id": "玩家名", "role": "T", "xinfa": "铁牢", "account": "策T-01", "time": "..."}]
        self.roster = []

    # --- 功能函数 ---
    
    def get_current_counts(self):
        """统计当前各职责人数"""
        counts = {"T": 0, "N": 0, "DPS": 0}
        for p in self.roster:
            counts[p['role']] += 1
        return counts

    def draw_character(self, player_id, proficient_roles):
        """
        核心抽签逻辑
        player_id: 玩家名字
        proficient_roles: 玩家会玩的心法列表 ["铁牢律(T)", "紫霞功"]
        """
        # 1. 检查是否已经抽过了
        for p in self.roster:
            if p['id'] == player_id:
                return False, f"你已经抽过号了！结果是：{p['xinfa']} - {p['account']}"

        # 2. 分析当前缺什么位置
        current_counts = self.get_current_counts()
        needed_roles = []
        for role, limit in self.TARGET_CONFIG.items():
            if current_counts[role] < limit:
                needed_roles.append(role)
        
        if not needed_roles:
            return False, "队伍已满员！(25/25)"

        # 3. 筛选玩家能玩的心法
        # 先给心法归类
        valid_candidates = [] # [{"xinfa": "铁牢", "role": "T", "account": "策T-01"}]
        
        for xinfa in proficient_roles:
            # 判断心法职责
            role = "DPS" # 默认为DPS
            if "(T)" in xinfa: role = "T"
            elif "(奶" in xinfa: role = "N"
            
            # 如果这个职责队伍不需要了，跳过
            if role not in needed_roles:
                continue
            
            # 检查号池里这个心法还有没有号
            accounts = self.ACCOUNT_POOL.get(xinfa, [])
            available_accs = [acc for acc in accounts if acc not in self.used_accounts]
            
            # 把所有可用账号加入候选池
            for acc in available_accs:
                valid_candidates.append({"xinfa": xinfa, "role": role, "account": acc})

        # 4. 进行抽签
        if not valid_candidates:
            # 失败原因分析
            return False, f"匹配失败！可能原因：\n1. 你的心法对应的职责已满（当前需求：{needed_roles}）\n2. 你会玩的心法号池里没号了"
        
        # 随机选一个
        choice = random.choice(valid_candidates)
        
        # 5. 锁定数据
        self.used_accounts.add(choice['account'])
        self.roster.append({
            "id": player_id,
            "role": choice['role'],
            "xinfa": choice['xinfa'],
            "account": choice['account'],
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        return True, choice

    def reset_game(self):
        """重置所有数据"""
        self.used_accounts = set()
        self.roster = []


# 初始化全局状态
game = GameState()

# ================= 2. 界面显示 =================

st.title("⚔️ 25人本 · 全自动发号中心")

# --- 侧边栏：实时监控 ---
with st.sidebar:
    st.header("📊 团队监控")
    counts = game.get_current_counts()
    
    # 进度条展示
    st.write(f"🛡️ 坦克 ({counts['T']}/2)")
    st.progress(min(counts['T']/2, 1.0))
    
    st.write(f"⚕️ 治疗 ({counts['N']}/4)")
    st.progress(min(counts['N']/4, 1.0))
    
    st.write(f"⚔️ 输出 ({counts['DPS']}/19)")
    st.progress(min(counts['DPS']/19, 1.0))
    
    st.divider()
    
    if st.button("⚠️ 管理员：重置所有数据"):
        game.reset_game()
        st.rerun()
    
    st.info("提示：所有人无需刷新，点击按钮会自动同步最新状态。")

# --- 主区域：玩家操作 ---
st.subheader("👤 玩家登记")

col1, col2 = st.columns([1, 2])

with col1:
    player_name = st.text_input("输入你的ID", placeholder="例如：卷卷")

with col2:
    # 获取所有心法选项
    all_xinfas = list(game.ACCOUNT_POOL.keys())
    selected_skills = st.multiselect("勾选你会玩的心法（号池里有的）", options=all_xinfas)

draw_btn = st.button("🎲 开始匹配", type="primary", use_container_width=True)

# 处理抽签逻辑
if draw_btn:
    if not player_name:
        st.toast("❌ 请先输入ID！")
    elif not selected_skills:
        st.toast("❌ 请至少选择一个心法！")
    else:
        success, result = game.draw_character(player_name, selected_skills)
        if success:
            st.balloons()
            st.success(f"🎉 **匹配成功！**\n\n分配给 **{player_name}** 的账号是：\n# 【{result['xinfa']}】 {result['account']}")
        else:
            st.error(result)

# --- 下方：实时大名单 ---
st.divider()
st.subheader("📋 实时大名单 (自动更新)")

if len(game.roster) > 0:
    # 转换成表格展示
    df = pd.DataFrame(game.roster)
    # 美化表格列名
    df.columns = ["玩家ID", "职责", "心法", "分配账号", "抽签时间"]
    
    # 按职责排序：T -> N -> DPS
    role_order = {"T": 0, "N": 1, "DPS": 2}
    df['order'] = df['职责'].map(role_order)
    df = df.sort_values('order').drop('order', axis=1)
    
    st.dataframe(
        df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "职责": st.column_config.TextColumn(
                "职责",
                help="T=坦克, N=治疗, DPS=输出",
                validate="^(T|N|DPS)$"
            )
        }
    )
else:
    st.info("暂无数据，快来抢首杀！")
