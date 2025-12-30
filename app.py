import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import yfinance as yf  # 引入做法 B：抓取台股名稱

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖戰報", layout="centered")

# 2. CSS 優化 (包含高解析度渲染與標題一行化)
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 22px !important; white-space: nowrap; overflow: hidden; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; color: #1f77b4; }
    .stAlert { padding: 0.5rem 1rem; margin-bottom: 8px; }
    .stDataFrame { image-rendering: -webkit-optimize-contrast !important; -webkit-font-smoothing: antialiased !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 核心功能：Tick 判斷
def get_tick(price):
    if price < 10: return 0.01
    elif price < 50: return 0.05
    elif price < 100: return 0.1
    elif price < 500: return 0.5
    elif price < 1000: return 1.0
    else: return 5.0

# 4. 側邊欄導覽
st.sidebar.title("🛠️ 功能選單")
page = st.sidebar.radio("請選擇功能", ["📊 即時精算", "📝 交易日誌"])

# --- 頁面 1：即時精算 (保留原本功能) ---
if page == "📊 即時精算":
    components.html("<script>window.parent.document.querySelectorAll('input[type=\"number\"]')[0].focus();</script>", height=0)
    st.title("🎯 Chris | 即時損益精算")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        buy_p = st.number_input("買入價格", value=None, step=0.05, placeholder="輸入價格")
    with col_in2:
        qty = st.number_input("購買張數", value=1, step=1)

    if buy_p:
        if 'd_val' not in st.session_state: st.session_state.d_val = 0.28
        st.divider()
        current_disc = st.slider(f"手續費 {st.session_state.d_val*10:.1f} 折", 0.1, 1.0, 0.28, step=0.01)
        st.session_state.d_val = current_disc
        
        # 計算逻辑... (略，保持與上一版一致)
        buy_fee = int(buy_p * qty * 1000 * 0.001425 * current_disc)
        total_cost = int((buy_p * qty * 1000) + buy_fee)
        be_p_raw = buy_p * (1 + (0.001425 * current_disc) * 2 + 0.0015)
        needed_ticks = 0; check_p = buy_p
        while check_p < be_p_raw:
            needed_ticks += 1; check_p += get_tick(check_p)
        final_be_p = check_p
        
        st.info(f"💡 向上跳 **{needed_ticks}** 檔 ({final_be_p:.2f}) 開始獲利")
        c1, c2 = st.columns(2)
        c1.metric("買入總成本", f"{total_cost:,} 元")
        c2.metric("保本價", f"{final_be_p:.2f}")

# --- 頁面 2：交易日誌 (初版) ---
elif page == "📝 交易日誌":
    st.title("📈 Chris | 當沖交易戰報")
    
    # 建立一個暫存的 session_state 來存放今天的交易
    if 'daily_logs' not in st.session_state:
        st.session_state.daily_logs = []

    with st.expander("➕ 新增一筆交易", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            symbol = st.text_input("股票代號", placeholder="例如: 2330")
        with c2:
            buy_price = st.number_input("買入價", min_value=0.0, step=0.05)
        with c3:
            sell_price = st.number_input("賣出價", min_value=0.0, step=0.05)
        
        c4, c5 = st.columns(2)
        with c4:
            log_qty = st.number_input("張數", min_value=1, step=1)
        with c5:
            # 自動帶出名稱的功能
            stock_name = "未確認"
            if symbol:
                try:
                    ticker = yf.Ticker(f"{symbol}.TW")
                    stock_name = ticker.info.get('longName') or ticker.info.get('shortName') or symbol
                except:
                    stock_name = "查無此代號"
            st.write(f"股票名稱：**{stock_name}**")

        if st.button("✅ 紀錄此筆交易"):
            # 計算該筆淨損益 (固定以 2.8 折計算，或可連動)
            disc = st.session_state.get('d_val', 0.28)
            b_cost = (buy_price * log_qty * 1000) + int(buy_price * log_qty * 1000 * 0.001425 * disc)
            s_rev = (sell_price * log_qty * 1000) - int(sell_price * log_qty * 1000 * 0.001425 * disc) - int(sell_price * log_qty * 1000 * 0.0015)
            net_profit = int(s_rev - b_cost)
            
            new_log = {
                "代號": symbol,
                "名稱": stock_name,
                "買入": buy_price,
                "賣出": sell_price,
                "張數": log_qty,
                "淨損益": net_profit
            }
            st.session_state.daily_logs.append(new_log)
            st.success("已加入今日戰報！")

    # 顯示今日統計
    if st.session_state.daily_logs:
        df_logs = pd.DataFrame(st.session_state.daily_logs)
        total_p = df_logs["淨損益"].sum()
        
        st.divider()
        st.subheader("📅 今日戰績匯總")
        st.metric("今日總盈虧", f"{total_p:,} 元", delta=f"{total_p}", delta_color="normal")
        
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ 清空今日紀錄"):
            st.session_state.daily_logs = []
            st.rerun()
    else:
        st.info("目前尚無交易紀錄，請於上方新增。")

    st.caption("註：目前為暫存版，網頁重新整理紀錄會消失。待測試後將串接 Google Sheets 永久儲存。")
