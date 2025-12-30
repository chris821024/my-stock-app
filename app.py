import streamlit as st
import pandas as pd

# 1. 網頁基本設定：Chris 專屬標題
st.set_page_config(page_title="Chris | 當沖損益精算", layout="centered")

# 2. 進階美化 CSS
st.markdown("""
    <style>
    /* 隱藏上方多餘空間 */
    .block-container { padding-top: 2rem; }
    /* 讓數字與文字更具質感 */
    div[data-testid="stMetricValue"] { font-size: 28px !important; }
    /* 設定背景為乾淨的白色 */
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 主標題 ---
st.title("🎯 Chris | 當沖損益精算")
st.caption("手續費固定 2.8 折｜證交稅 0.15% (當沖減半)")

# --- 4. 手機優化輸入區：直接置頂並排 ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    buy_p = st.number_input("買入價格", value=None, step=0.05, placeholder="輸入價格")
with col_in2:
    qty = st.number_input("購買張數", value=1, step=1)

# --- 5. 計算邏輯 ---
if buy_p:
    # 判斷台股 Tick 大小
    if buy_p < 50: tick = 0.05
    elif buy_p < 100: tick = 0.05
    elif buy_p < 500: tick = 0.5
    else: tick = 1.0

    disc = 0.28
    buy_fee = int(buy_p * qty * 1000 * 0.001425 * disc)
    total_cost = int((buy_p * qty * 1000) + buy_fee)
    
    # 計算保本點
    be_p_raw = buy_p * (1 + (0.001425 * disc) * 2 + 0.0015)
    needed_ticks = 0
    while (buy_p + (needed_ticks * tick)) < be_p_raw:
        needed_ticks += 1
    final_be_p = buy_p + (needed_ticks * tick)

    # --- 6. 核心數據看板 ---
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("買入總成本", f"{total_cost:,} 元")
    c2.metric("損益平衡價", f"{final_be_p:.2f}")

    # 風險指示燈
    if needed_ticks <= 1:
        st.success(f"🟢 低風險｜跳 {needed_ticks} 檔即保本")
    elif needed_ticks <= 2:
        st.warning(f"🟡 中風險｜跳 {needed_ticks} 檔保本")
    else:
        st.error(f"🔴 高風險｜跳 {needed_ticks} 檔才保本")

    # --- 7. 雙向損益水溫計 (表格優化) ---
    data = []
    for i in range(5, -6, -1):
        s_p = buy_p + (i * tick)
        s_total = s_p * qty * 1000
        s_fee = int(s_total * 0.001425 * disc)
        tax = int(s_total * 0.0015)
        net = int(s_total - s_fee - tax - total_cost)
        
        label = f"+{i} 檔" if i > 0 else (f"-{abs(i)} 檔" if i < 0 else "🎯 買入價")
        trend = "📈" if net > 0 else ("📉" if net < 0 else "➖")
        
        data.append({
            "市場動態": label,
            "建議賣價": f"{s_p:.2f}",
            "預估盈虧": net,
            "報酬率": f"{(net/total_cost)*100:.2f}% {trend}"
        })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        column_config={
            "預估盈虧": st.column_config.NumberColumn("實際損益", format="%d 元"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.caption(f"💡 每跳一檔損益約：{int(tick * qty * 1000):,} 元")

else:
    st.info("👋 盤中交易愉快！請直接在上方輸入買入價格。")
