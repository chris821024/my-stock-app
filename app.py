import streamlit as st
import pandas as pd

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖損益精算", layout="centered")

# 2. CSS 優化
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h1 { 
        font-size: 22px !important; 
        white-space: nowrap; 
    }
    div[data-testid="stMetricValue"] { font-size: 26px !important; color: #1f77b4; }
    .stAlert { padding: 0.5rem 1rem; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 主標題 ---
st.title("🎯 Chris | 當沖損益精算")

# --- 4. 置頂輸入區 ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    buy_p = st.number_input("買入價格", value=None, step=0.05, placeholder="輸入價格")
with col_in2:
    qty = st.number_input("購買張數", value=1, step=1)

# --- 5. 計算與顯示邏輯 ---
if buy_p:
    # 決定底部的拉條數值 (使用 session_state 保持狀態)
    if 'd_val' not in st.session_state:
        st.session_state.d_val = 0.28
    
    # 先建立一個容器，等等把結果塞回輸入框下方
    result_container = st.container()

    # 底部拉條與資訊區
    st.write("") 
    st.divider()
    current_disc = st.slider(f"手續費 {st.session_state.d_val*10:.1f} 折 (滑動調整)", 0.1, 1.0, 0.28, step=0.01)
    st.session_state.d_val = current_disc
    st.caption(f"📌 交易設定參考：手續費 {current_disc*10:.1f} 折 ｜ 當沖稅率 0.15%")

    # 執行計算
    tick = 0.05 if buy_p < 100 else (0.5 if buy_p < 500 else 1.0)
    buy_fee = int(buy_p * qty * 1000 * 0.001425 * current_disc)
    total_cost = int((buy_p * qty * 1000) + buy_fee)
    
    be_p_raw = buy_p * (1 + (0.001425 * current_disc) * 2 + 0.0015)
    needed_ticks = 0
    while (buy_p + (needed_ticks * tick)) < be_p_raw:
        needed_ticks += 1
    final_be_p = buy_p + (needed_ticks * tick)

    # 將結果塞入容器 (顯示在輸入框與拉條之間)
    with result_container:
        st.info(f"💡 每跳一檔損益：{int(tick * qty * 1000):,} 元")
        st.info(f"💡 向上跳 **{needed_ticks}** 檔 ({final_be_p:.2f}) 開始獲利")
        
        c1, c2 = st.columns(2)
        c1.metric("買入總成本", f"{total_cost:,} 元")
        c2.metric("保本價", f"{final_be_p:.2f}")

        # 表格製作
        data = []
        for i in range(5, -6, -1):
            s_p = buy_p + (i * tick)
            s_total = s_p * qty * 1000
            s_fee = int(s_total * 0.001425 * current_disc)
            tax = int(s_total * 0.0015)
            net = int(s_total - s_fee - tax - total_cost)
            label = f"+{i} 檔" if i > 0 else (f"-{abs(i)} 檔" if i < 0 else "🎯 買入價")
            trend = "📈" if net > 0 else ("📉" if net < 0 else "➖")
            data.append({"跳動": label, "賣出價": f"{s_p:.2f}", "預估損益": net, "報酬%": f"{(net/total_cost)*100:.2f}% {trend}"})
        
        st.dataframe(pd.DataFrame(data), column_config={"預估損益": st.column_config.NumberColumn("實際損益", format="%d 元")}, hide_index=True, use_container_width=True)

else:
    st.info("👋 歡迎！請在上方輸入買入價格開始測算。")
