import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import yfinance as yf

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖戰報", layout="centered")

# 2. CSS 渲染優化
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 22px !important; white-space: nowrap; overflow: hidden; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 內建核心 500+ 標的 (縮略版，包含熱門股) ---
@st.cache_resource
def get_stock_db():
    return {
        "2485": "兆赫", "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2303": "聯電",
        "2603": "長榮", "2609": "陽明", "2615": "萬海", "2618": "長榮航", "2610": "華航",
        "3231": "緯創", "2382": "廣達", "2376": "技嘉", "2356": "英業達", "1513": "中興電",
        "1519": "華城", "1504": "東元", "1605": "華新", "2409": "友達", "3481": "群創",
        "2363": "矽統", "2368": "金像電", "2313": "華通", "3037":"欣興", "1514":"亞力"
        # 系統會自動擴充搜尋
    }

@st.cache_data(ttl=86400)
def fetch_api_name(sym):
    try:
        for s in [".TW", ".TWO"]:
            t = yf.Ticker(f"{sym}{s}")
            n = t.info.get('shortName') or t.info.get('longName')
            if n: return n
    except: return None
    return None

# 4. 側邊欄與導覽
page = st.sidebar.radio("功能導覽", ["📊 即時精算", "📝 交易日誌"])

# --- 頁面 1：即時精算 (略) ---
if page == "📊 即時精算":
    components.html("<script>window.parent.document.querySelectorAll('input[type=\"number\"]')[0].focus();</script>", height=0)
    st.title("🎯 Chris | 即時損益精算")
    # ... 原有功能代碼 ...
    p1, p2 = st.columns(2)
    with p1: b_p = st.number_input("買入價格", value=None, step=0.05)
    with p2: b_q = st.number_input("購買張數", value=1, step=1)
    if b_p:
        if 'd' not in st.session_state: st.session_state.d = 0.28
        disc = st.slider(f"手續費 {st.session_state.d*10:.1f} 折", 0.1, 1.0, 0.28)
        st.session_state.d = disc
        cost = int(b_p * b_q * 1000 * (1 + 0.001425 * disc))
        st.metric("買入總成本", f"{cost:,} 元")

# --- 頁面 2：交易日誌 (加入手動輸入功能) ---
elif page == "📝 交易日誌":
    st.title("📈 Chris | 當沖交易戰報")
    if 'logs' not in st.session_state: st.session_state.logs = []

    with st.expander("➕ 新增交易紀錄", expanded=True):
        c1, c2, c3 = st.columns([1,1,1])
        with c1: sym = st.text_input("股票代號", placeholder="例如: 2485")
        with c2: lp = st.number_input("買入價", min_value=0.0, step=0.05, key="lp_log")
        with c3: ls = st.number_input("賣出價", min_value=0.0, step=0.05, key="ls_log")
        
        lq = st.number_input("張數", min_value=1, step=1, key="lq_log")
        
        # 智能名稱辨識邏輯
        auto_name = ""
        if sym:
            db = get_stock_db()
            if sym in db:
                auto_name = db[sym]
            else:
                auto_name = fetch_api_name(sym) or "查無代號"
        
        # --- 手動校正空格 ---
        custom_name = st.text_input("股票名稱 (若搜尋不到請手動修改)", value=auto_name)
        final_name = custom_name if custom_name else auto_name

        if st.button("✅ 儲存此筆交易"):
            d = st.session_state.get('d', 0.28)
            bc = (lp * lq * 1000) + int(lp * lq * 1000 * 0.001425 * d)
            sr = (ls * lq * 1000) - int(ls * lq * 1000 * 0.001425 * d) - int(ls * lq * 1000 * 0.0015)
            net = int(sr - bc)
            st.session_state.logs.append({"代號": sym, "名稱": final_name, "張數": lq, "損益": net})
            st.rerun()

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.divider()
        st.metric("今日總盈虧", f"{df['損益'].sum():,} 元")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("🗑️ 清空今日戰報"):
            st.session_
