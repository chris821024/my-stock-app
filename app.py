import streamlit as st
import pandas as pd

# 1. 網頁設定：改為自動寬度，方便手機閱讀
st.set_page_config(page_title="2.8折快閃計算器", layout="centered")

# 自定義 CSS：強化手機版視覺與顏色
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    /* 讓數字大一點，方便手機看 */
    div[data-testid="stMetricValue"] { font-size: 32px !important; font-weight: bold; }
    /* 調整表格字體 */
    .stDataFrame { font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 輸入區：直接放在主頁面最上方 (不再使用側邊欄) ---
st.title("⚖️ 當沖損益快閃計")

col_in1, col_in2 = st.columns(2)
with col_in1:
    buy_p = st.number_input("買入價", value=None, step=0.05, placeholder="輸入價格")
with col_in2:
    qty = st.number_input("張數", value=1, step=1)

# --- 3. 計算邏輯 ---
if buy_p:
    # 判斷台股 Tick 大小
    if buy_p < 50: tick = 0.05
    elif buy_p < 100: tick = 0.05
    elif buy_p < 500: tick = 0.5
    else: tick = 1.0

    disc = 0.28 # 固定 2.8 折
    buy_fee = int(buy_p * qty * 1000 * 0.001425 * disc)
    total_cost = int((buy_p * qty * 1000) + buy_fee)
    
    # 計算保本點
    be_p_raw = buy_p * (1 + (0.001425 * disc) * 2 + 0.0015)
    needed_ticks = 0
    while (buy_p + (needed_ticks * tick)) < be_p_raw:
        needed_ticks += 1
    final_be_p = buy_p + (needed_ticks * tick)

    # --- 4. 顯示結果：風險燈號 ---
    if needed_ticks <= 1:
        st.success(f"🟢 低風險｜跳 {needed_ticks} 檔 ({final_be_p:.2f}) 保本")
    elif needed_ticks <= 2:
        st.warning(f"🟡 中風險｜跳 {needed_ticks} 檔 ({final_be_p:.2f}) 保本")
    else:
        st.error(f"🔴 高風險｜跳 {needed_ticks} 檔 ({final_be_p:.2f}) 保本")

    # 數據看板
    c1, c2 = st.columns(2)
    c1.metric("總成本", f"{total_cost:,}")
    c2.metric("保本價", f"{final_be_p:.2f}")

    # --- 5. 漲跌雙向表格 ---
    data = []
    # 範圍縮小至 漲跌各 5 檔，讓手機不用滑太久
    for i in range(5, -6, -1):
        s_p = buy_p + (i * tick)
        s_total = s_p * qty * 1000
        s_fee = int(s_total * 0.001425 * disc)
        tax = int(s_total * 0.0015)
        net = int(s_total - s_fee - tax - total_cost)
        
        # 簡化標籤，節省手機螢幕空間
        icon = "+" if i > 0 else ("-" if i < 0 else "0")
        label = f"{icon}{abs(i)} 檔" if i != 0 else "買入價"
        
        # 報酬率加上顏色符號
        color_icon = "📈" if net > 0 else ("📉" if net < 0 else "➖")
        
        data.append({
            "變動": label,
            "價格": f"{s_p:.2f}",
            "損益": net,
            "報酬%": f"{(net/total_cost)*100:.2f}% {color_icon}"
        })

    df = pd.DataFrame(data)

    # 使用新的 st.dataframe 讓手機閱讀更順暢
    st.dataframe(
        df,
        column_config={
            "變動": st.column_config.TextColumn("跳動"),
            "價格": st.column_config.TextColumn("賣出價"),
            "損益": st.column_config.NumberColumn("盈虧", format="%d 元"),
            "報酬%": "報酬"
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.caption(f"💡 每跳一檔損益約：{int(tick * qty * 1000):,} 元")

else:
    st.info("💡 請直接輸入「買入價格」開始計算")
