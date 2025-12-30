import streamlit as st
import pandas as pd

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖損益精算", layout="centered")

# 2. CSS 優化：確保手機版標題與燈泡提示清晰
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    /* 強制標題在手機上不換行 */
    h1 { 
        font-size: 24px !important; 
        white-space: nowrap; 
        overflow: hidden;
        text-overflow: ellipsis;
    }
    div[data-testid="stMetricValue"] { font-size: 28px !important; color: #1f77b4; }
    .main { background-color: #ffffff; }
    .stAlert { padding: 0.5rem 1rem; margin-bottom: 5px; }
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

# 新增：手續費折扣拉條 (預設 0.28)
disc = st.slider("手續費折扣 (預設 2.8 折)", 0.1, 1.0, 0.28, step=0.01)

# --- 5. 計算邏輯 ---
if buy_p:
    # 判斷台股 Tick 大小
    if buy_p < 50: tick = 0.05
    elif buy_p < 100: tick = 0.05
    elif buy_p < 500: tick = 0.5
    else: tick = 1.0

    # 使用拉條取得的 disc
    buy_fee = int(buy_p * qty * 1000 * 0.001425 * disc)
    total_cost = int((buy_p * qty * 1000) + buy_fee)
    
    # 計算保本點
    be_p_raw = buy_p * (1 + (0.001425 * disc) * 2 + 0.0015)
    needed_ticks = 0
    while (buy_p + (needed_ticks * tick)) < be_p_raw:
        needed_ticks += 1
    final_be_p = buy_p + (needed_ticks * tick)

    # --- 6. 核心數據呈現 ---
    st.divider()
    
    # 兩行燈泡提示
    st.info(f"💡 每跳一檔損益：{int(tick * qty * 1000):,} 元")
    st.info(f"💡 向上跳 **{needed_ticks}** 檔 ({final_be_p:.2f}) 開始獲利")

    c1, c2 = st.columns(2)
    c1.metric("買入總成本", f"{total_cost:,} 元")
    c2.metric("保本價", f"{final_be_p:.2f}")

    # --- 7. 雙向損益表 ---
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
            "賣出價": f"{s_p:.2f}",
            "預估損益": net,
            "報酬%": f"{(net/total_cost)*100:.2f}% {trend}"
        })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        column_config={
            "預估損益": st.column_config.NumberColumn("實際損益", format="%d 元"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.caption(f"公式參考：手續費 {disc*10:.1f} 折 / 當沖稅率 0.15%")

else:
    st.info("👋 歡迎！請在上方輸入買入價格開始測算。")
