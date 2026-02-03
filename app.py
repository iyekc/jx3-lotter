import streamlit as st
import random
import pandas as pd
from datetime import datetime

# ================= 配置网页 =================
st.set_page_config(page_title="卷卷·换号普通发号机", page_icon="😈", layout="wide")

# ================= 1. 核心数据与全局状态 =================
@st.cache_resource
class GameState:
    def __init__(self):
        # 预设号池：格式 {"心法": ["账号A", "账号B"]}
        self.ACCOUNT_POOL = {
            "铁牢律(T)": ["绛晚秋",],
            "洗髓经(T)": ["福园的小菠萝"],
            "明尊琉璃体(T)": ["存乐"],
            "铁骨衣(T)": ["奶补"],
            
            "离经易道(奶花)": ["淼淼淼"],
            "云裳心经(奶秀)": ["雀盈杉"],
            "补天诀(奶毒)": ["毒奶-01", "毒奶-02"],
            "相知(奶歌)": ["不愧君"],
            "灵素(奶药)": ["夜合"],
            
            "紫霞功(气纯)": ["气纯-01", "气纯-02", "气纯-03"],
            "太虚剑意(剑纯)": ["剑纯-01"],
            "花间游": ["淮素@青梅煮酒"],
            "易筋经(和尚)": ["福园的大猫头"],
            "冰心诀": ["一只可爱兔兔", "冰心-02", "冰心-03"],
            "傲血战意": ["天策-01"],
            "问水/山居(藏剑)": ["藏剑-01", "藏剑-02"],
            "毒经": ["毒经-01"],
            "惊羽诀": ["鲸鱼-01"],
            "天罗诡道(田螺)": ["田螺-01", "田螺-02"],
            "焚影圣诀": ["明教-01"],
            "笑尘诀": ["丐瑁"],
            "分山劲": ["苍云-01"],
            "莫问": ["夜笙笙"],
            "北傲诀": ["柳倦"],
            "凌海诀": ["抑郁伞爹"],
            "隐龙诀": ["凌雪-01"],
            "太玄经": ["天钺熠巡使"],
            "无方": ["小方我就这样"],
            "孤锋诀": ["刀宗-01"],
            "山海心诀": ["万灵-01"],
            "无相楼": ["柳花卷"],
            "周天诀": ["宴山卿"]
        }
        
        # 目标配置
        self.TARGET_CONFIG = {"T": 2, "N": 4, "DPS": 19}
        
        # 已使用账号记录
        self.used_accounts = set()
        
        # 玩家名单
        self.roster = []

    # --- 辅助：判断职责 ---
    def get_role_type(self, xinfa_name):
        if "(T)" in xinfa_name: return "T"
        if "(奶" in xinfa_name: return "N"
        return "DPS"

    # --- 功能函数 ---
    def get_current_counts(self):
        """统计当前各职责人数"""
        counts = {"T": 0, "N": 0, "DPS": 0}
        for p in self.roster:
            counts[p['role']] += 1
        return counts

    def draw_character(self, player_id, known_roles):
        """
        核心抽签逻辑 (痛苦号版)
        player_id: 玩家名字
        known_roles: 玩家会玩的心法列表 (这些要被排除！！)
        """
        # 1. 检查是否已经抽过了
        for p in self.roster:
            if p['id'] == player_id:
                return False, f"你已经抽过号了！你的痛苦是：{p['xinfa']} - {p['account']}"

        # 2. 分析当前缺什么位置
        current_counts = self.get_current_counts()
        needed_roles = []
        for role, limit in self.TARGET_CONFIG.items():
            if current_counts[role] < limit:
                needed_roles.append(role)
        
        if not needed_roles:
            return False, "队伍已满员！(25/25)"

        # 3. 筛选玩家 **不会玩** 的心法 (Valid Candidates)
        # 逻辑：遍历所有号池心法 -> 排除known_roles -> 排除不需要的职责 -> 排除没号的
        
        valid_candidates = [] 
        all_xinfas = list(self.ACCOUNT_POOL.keys())
        
        for xinfa in all_xinfas:
            # === 核心修改点 ===
            # 如果这个心法在“会玩列表”里，跳过 (我不想要会玩的)
            if xinfa in known_roles:
                continue
            # ================
            
            # 判断心法职责
            role = self.get_role_type(xinfa)
            
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
            return False, f"无号可抽！可能原因：\n1. 你会的太多了（全职高手？）\n2. 你不会玩的那几个职业，号都被抽光了\n3. 剩下的位置（{needed_roles}）刚好是你全都会的"
        
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

st.title("😈 2卷卷 · 换号普通发号机")
st.caption("规则：勾选你会玩的心法，系统会**避开**它们！")

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
    
    st.info("提示：点击按钮会自动同步最新状态。")

# --- 主区域：玩家操作 ---
st.subheader("👤 接受审判")

col1, col2 = st.columns([1, 2])

with col1:
    player_name = st.text_input("输入你的ID", placeholder="例如：卷卷")

with col2:
    # 获取所有心法选项
    all_xinfas = list(game.ACCOUNT_POOL.keys())
    # 这里的提示语改了
    selected_skills = st.multiselect("勾选你 **熟练/会玩** 的心法（这些将被 **排除**！）", options=all_xinfas)

draw_btn = st.button("🔥 开始痛苦面具", type="primary", use_container_width=True)

# 处理抽签逻辑
if draw_btn:
    if not player_name:
        st.toast("❌ 请先输入ID！")
    else:
        # 注意：这里传进去的是 selected_skills (会玩的)，逻辑里会排除它们
        success, result = game.draw_character(player_name, selected_skills)
        if success:
            st.balloons()
            st.success(f"🎉 **匹配成功！你将使用的号是：**\n\n### 【{result['xinfa']}】 {result['account']}\n\n加油！别翻车！")
        else:
            st.error(result)

# --- 下方：实时大名单 ---
st.divider()
st.subheader("📋 实时受害者名单")

if len(game.roster) > 0:
    # 转换成表格展示
    df = pd.DataFrame(game.roster)
    # 美化表格列名
    df.columns = ["玩家ID", "分配职责", "心法", "账号", "抽签时间"]
    
    # 按职责排序：T -> N -> DPS
    role_order = {"T": 0, "N": 1, "DPS": 2}
    df['order'] = df['分配职责'].map(role_order)
    df = df.sort_values('order').drop('order', axis=1)
    
    st.dataframe(
        df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "分配职责": st.column_config.TextColumn(
                "分配职责",
                help="T=坦克, N=治疗, DPS=输出",
                validate="^(T|N|DPS)$"
            )
        }
    )
else:
    st.info("暂无数据！")
