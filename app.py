import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import yfinance as yf

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖戰報", layout="centered")

# 2. CSS 優化 (包含高解析度渲染與標題一行化)
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 22px !important; white-space: nowrap; overflow: hidden; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; color: #1f77b4; }
    .stAlert { padding: 0.5rem 1rem; margin-bottom: 8px; }
    /* 強化解析度 */
    .stDataFrame, [data-testid="stTable"] {
        image-rendering: -webkit-optimize-contrast !important;
        -webkit-font-smoothing: antialiased !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 核心函數：Tick 判斷
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

# --- 頁面 1：即時精算 ---
if page == "📊 即時精算":
    # 自動對焦腳本
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
        
        # 顯示跳動表格
        data = []
        up_p = []; curr_up = buy_p
        for _ in range(5): curr_up += get_tick(curr_up); up_p.append(curr_up)
        down_p = []; curr_down = buy_p
        for _ in range(5): curr_down -= get_tick(curr_down - 0.01); down_p.append(curr_down)
        
        for p in up_p[::-1] + [buy_p] + down_p:
            s_total = p * qty * 1000
            s_fee = int(s_total * 0.001425 * current_disc)
            tax = int(s_total * 0.0015)
            net = int(s_total - s_fee - tax - total_cost)
            trend = "📈" if net > 0 else ("📉" if net < 0 else "➖")
            data.append({"賣出價": f"{p:.2f}", "實際損益": net, "報酬%": f"{(net/total_cost)*100:.2f}% {trend}"})
        st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

# --- 頁面 2：交易日誌 ---
elif page == "📝 交易日誌":
    st.title("📈 Chris | 當沖交易戰報")
    
    if 'daily_logs' not in st.session_state:
        st.session_state.daily_logs = []

    with st.expander("➕ 新增一筆交易", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            symbol = st.text_input("股票代號", placeholder="例如: 2485")
        with c2:
            l_buy = st.number_input("買入價", min_value=0.0, step=0.05)
        with c3:
            l_sell = st.number_input("賣出價", min_value=0.0, step=0.05)
        
        c4, c5 = st.columns(2)
        with c4:
            l_qty = st.number_input("張數", min_value=1, step=1)
        with c5:
            stock_name = "未確認"
            if symbol:
                try:
                    # 先試上市 (.TW)，再試上櫃 (.TWO)
                    t = yf.Ticker(f"{symbol}.TW")
                    stock_name = t.info.get('longName') or t.info.get('shortName')
                    if not stock_name:
                        t = yf.Ticker(f"{symbol}.TWO")
                        stock_name = t.info.get('longName') or t.info.get('shortName')
                except:
                    stock_name = "搜尋中..."
            st.write(f"股票名稱：**{stock_name or '查無代號'}**")

        if st.button("✅ 紀錄此筆交易"):
            disc = st.session_state.get('d_val', 0.28)
            b_cost = (l_buy * l_qty * 1000) + int(l_buy * l_qty * 1000 * 0.001425 * disc)
            s_rev = (l_sell * l_qty * 1000) - int(l_sell * l_qty * 1000 * 0.001425 * disc) - int(l_sell * l_qty * 1000 * 0.0015)
            net_profit = int(s_rev - b_cost)
            st.session_state.daily_logs.append({"代號": symbol, "名稱": stock_name, "淨損益": net_profit})
            st.success("已紀錄！")

    if st.session_state.daily_logs:
        df = pd.DataFrame(st.session_state.daily_logs)
        st.metric("今日總盈虧", f"{df['淨損益'].sum():,} 元")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("🗑️ 清空紀錄"):
            st.session_state.daily_logs = []; st.rerun()
