import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖戰報", layout="centered")

# 2. CSS 強化：解決表格模糊 + 字體清晰
st.markdown("""
    <style>
    .stDataFrame, [data-testid="stTable"] {
        image-rendering: -webkit-optimize-contrast !important;
        -webkit-font-smoothing: antialiased !important;
    }
    .stDataFrame td, .stDataFrame th {
        font-size: 15px !important;
        font-weight: 500 !important;
    }
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 24px !important; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 核心數據庫 (核心 500+ 標的)
@st.cache_resource
def load_all_stocks():
    return {
        "2485": "兆赫", "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2303": "聯電",
        "2603": "長榮", "2609": "陽明", "2615": "萬海", "2618": "長榮航", "2610": "華航",
        "3231": "緯創", "2382": "廣達", "2376": "技嘉", "2356": "英業達", "1513": "中興電",
        "1519": "華城", "1504": "東元", "1605": "華新", "2409": "友達", "3481": "群創",
        "1514": "亞力", "2363": "矽統", "2368": "金像電", "2313": "華通", "3037": "欣興"
    }

# 4. Tick 判斷邏輯
def get_tick(p):
    if p < 10: return 0.01
    elif p < 50: return 0.05
    elif p < 100: return 0.1
    elif p < 500: return 0.5
    elif p < 1000: return 1.0
    else: return 5.0

# 5. 分頁導覽
page = st.sidebar.radio("功能選單", ["📊 即時精算", "📝 交易日誌"])

# --- 頁面 1：即時精算 (已補回表格) ---
if page == "📊 即時精算":
    components.html("<script>window.parent.document.querySelectorAll('input[type=\"number\"]')[0].focus();</script>", height=0)
    st.title("🎯 Chris | 即時損益精算")
    p1, p2 = st.columns(2)
    with p1: b_p = st.number_input("買入價格", value=None, step=0.05)
    with p2: b_q = st.number_input("購買張數", value=1, step=1)
    
    if b_p:
        if 'd' not in st.session_state: st.session_state.d = 0.28
        disc = st.slider(f"手續費 {st.session_state.d*10:.1f} 折", 0.1, 1.0, 0.28)
        st.session_state.d = disc
        
        # 基本計算
        cost = int(b_p * b_q * 1000 * (1 + 0.001425 * disc))
        be_raw = b_p * (1 + (0.001425 * disc) * 2 + 0.0015)
        cp = b_p; tk = 0
        while cp < be_raw: tk += 1; cp += get_tick(cp)
        
        st.info(f"💡 向上跳 **{tk}** 檔 ({cp:.2f}) 開始獲利")
        st.metric("買入總成本", f"{cost:,} 元")

        # --- 補回：跳動損益表格 ---
        st.write("### 📈 預估損益對照表")
        data = []
        up_ps = []; cur_u = b_p
        for _ in range(5): cur_u += get_tick(cur_u); up_ps.append(cur_u)
        down_ps = []; cur_d = b_p
        for _ in range(5): cur_d -= get_tick(cur_d - 0.01); down_ps.append(cur_d)
        
        for p in up_ps[::-1] + [b_p] + down_ps:
            s_total = p * b_q * 1000
            s_fee = int(s_total * 0.001425 * disc)
            tax = int(s_total * 0.0015)
            net = int(s_total - s_fee - tax - cost)
            trend = "🔴" if net > 0 else ("🟢" if net < 0 else "➖")
            data.append({
                "賣出價": f"{p:.2f}",
                "預估損益": net,
                "報酬%": f"{(net/cost)*100:.2f}% {trend}"
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# --- 頁面 2：交易日誌 ---
elif page == "📝 交易日誌":
    st.title("📈 Chris | 當沖交易戰報")
    if 'logs' not in st.session_state: st.session_state.logs = []
    stock_db = load_all_stocks()

    with st.expander("➕ 新增交易紀錄", expanded=True):
        c1, c2 = st.columns(2)
        with c1: sym = st.text_input("股票代號")
        with c2: lq = st.number_input("成交張數", min_value=1, step=1, value=1)
        
        c3, c4 = st.columns(2)
        with c3: lp = st.number_input("買入價", min_value=0.0, step=0.05, key="lp_log")
        with c4: ls = st.number_input("賣出價", min_value=0.0, step=0.05, key="ls_log")
        
        found_name = stock_db.get(sym, "")
        final_name = st.text_input("股票名稱 (找不到請手動填寫)", value=found_name)

        if st.button("✅ 儲存此筆戰報"):
            if not final_name and sym: final_name = sym
            d = st.session_state.get('d', 0.28)
            bc = (lp * lq * 1000) + int(lp * lq * 1000 * 0.001425 * d)
            sr = (ls * lq * 1000) - int(ls * lq * 1000 * 0.001425 * d) - int(ls * lq * 1000 * 0.0015)
            net = int(sr - bc)
            st.session_state.logs.append({"代號": sym, "名稱": final_name, "張數": lq, "損益": net})
            st.rerun()

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        total_p = df['損益'].sum()
        st.divider()
        st.metric(label="今日損益", value=f"{total_p:,} 元", delta=f"{total_p:,}",
                  delta_color="normal" if total_p >= 0 else "inverse")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("🗑️ 清空紀錄"): st.session_state.logs = []; st.rerun()
