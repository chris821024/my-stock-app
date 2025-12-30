import streamlit as st
import pandas as pd

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖損益精算", layout="centered")

# 2. CSS 優化
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 22px !important; white-space: nowrap; overflow: hidden; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; color: #1f77b4; }
    .stAlert { padding: 0.5rem 1rem; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 核心函數：精確判斷台股 Tick
def get_tick(price):
    if price < 10: return 0.01
    elif price < 50: return 0.05
    elif price < 100: return 0.1
    elif price < 500: return 0.5
    elif price < 1000: return 1.0
    else: return 5.0

# --- 4. 主標題 ---
st.title("🎯 Chris | 當沖損益精算")

# --- 5. 置頂輸入區 ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    buy_p = st.number_input("買入價格", value=None, step=0.05, placeholder="輸入價格")
with col_in2:
    qty = st.number_input("購買張數", value=1, step=1)

# --- 6. 計算與顯示邏輯 ---
if buy_p:
    # 確保 session state 有數值
    if 'd_val' not in st.session_state:
        st.session_state.d_val = 0.28
    
    # 建立結果顯示容器
    res_box = st.container()

    # 底部拉條區
    st.divider()
    current_disc = st.slider(f"手續費 {st.session_state.d_val*10:.1f} 折 (滑動調整)", 0.1, 1.0, 0.28, step=0.01)
    st.session_state.d_val = current_disc
    st.caption(f"📌 當前設定：手續費 {current_disc*10:.1f} 折 ｜ 當沖稅率 0.15%")

    # 執行精確計算
    buy_fee = int(buy_p * qty * 1000 * 0.001425 * current_disc)
    total_cost = int((buy_p * qty * 1000) + buy_fee)
    
    # 計算保本點 (考量動態 Tick 跨區間)
    be_p_raw = buy_p * (1 + (0.001425 * current_disc) * 2 + 0.0015)
    needed_ticks = 0
    check_p = buy_p
    while check_p < be_p_raw:
        needed_ticks += 1
        check_p += get_tick(check_p)
    final_be_p = check_p

    # 將結果塞回上方容器
    with res_box:
        st.info(f"💡 向上跳 **{needed_ticks}** 檔 ({final_be_p:.2f}) 開始獲利")
        
        c1, c2 = st.columns(2)
        c1.metric("買入總成本", f"{total_cost:,} 元")
        c2.metric("保本價", f"{final_be_p:.2f}")

        # 建立跨區間表格數據
        data = []
        up_prices = []
        curr_up = buy_p
        for _ in range(5):
            curr_up += get_tick(curr_up)
            up_prices.append(curr_up)
        
        down_prices = []
        curr_down = buy_p
        for _ in range(5):
            curr_down -= get_tick(curr_down - 0.01)
            down_prices.append(curr_down)
        
        all_p = up_prices[::-1] + [buy_p] + down_prices
        
        for p in all_p:
            s_total = p * qty * 1000
            s_fee = int(s_total * 0.001425 * current_disc)
            tax = int(s_total * 0.0015)
            net = int(s_total - s_fee - tax - total_cost)
            
            # 計算距離幾檔
            diff = 0
            if p > buy_p:
                tmp = buy_p
                while tmp < p:
                    tmp += get_tick(tmp); diff += 1
            elif p < buy_p:
                tmp = buy_p
                while tmp > p:
                    tmp -= get_tick(tmp - 0.01); diff -= 1
            
            label = f"+{int(diff)} 檔" if diff > 0 else (f"-{int(abs(diff))} 檔" if diff < 0 else "🎯 買入價")
            trend = "📈" if net > 0 else ("📉" if net < 0 else "➖")
            
            data.append({
                "跳動": label, 
                "賣出價": f"{p:.2f}", 
                "實際盈虧": net, 
                "報酬%": f"{(net/total_cost)*100:.2f}% {trend}"
            })
        
        st.dataframe(pd.DataFrame(data), column_config={"實際盈虧": st.column_config.NumberColumn("實際損益 (元)", format="%d")}, hide_index=True, use_container_width=True)

else:
    st.info("👋 歡迎！請在上方輸入買入價格開始測算。")
