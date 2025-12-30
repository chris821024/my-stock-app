import streamlit as st

# 設定網頁顯示
st.set_page_config(page_title="2.8折當沖計算器", layout="wide")
st.title("⚖️ 專屬當沖雙向損益計 (2.8折版)")

# 側邊欄
with st.sidebar:
    st.header("📊 盤中參數")
    buy_p = st.number_input("買入價格", value=None, step=0.05, placeholder="請輸入價格")
    qty = st.number_input("購買張數", value=1, step=1)
    disc = 0.28 # 固定 2.8 折
    st.write(f"當前設定：**手續費 2.8 折**")
    st.divider()
    st.info("💡 操作提示：\n輸入買價後，下方會自動顯示漲跌各 5 檔的精確損益。")

if buy_p:
    # 1. 判斷 Tick 大小
    if buy_p < 50: tick = 0.05
    elif buy_p < 100: tick = 0.05
    elif buy_p < 500: tick = 0.5
    else: tick = 1.0

    # 2. 計算成本與保本價
    buy_fee = int(buy_p * qty * 1000 * 0.001425 * disc)
    total_cost = int((buy_p * qty * 1000) + buy_fee)
    be_p_raw = buy_p * (1 + (0.001425 * disc) * 2 + 0.0015)
    needed_ticks = 0
    while (buy_p + (needed_ticks * tick)) < be_p_raw:
        needed_ticks += 1
    final_be_p = buy_p + (needed_ticks * tick)

    # 3. 風險燈號區
    if needed_ticks <= 1:
        st.success(f"🟢 低風險：跳 {needed_ticks} 檔 ({final_be_p:.2f}) 即保本。極具優勢！")
    elif needed_ticks <= 2:
        st.warning(f"🟡 中風險：跳 {needed_ticks} 檔 ({final_be_p:.2f}) 才保本。")
    else:
        st.error(f"🔴 高風險：跳 {needed_ticks} 檔 ({final_be_p:.2f}) 才保本。成本極重！")

    # 4. 關鍵數據看板
    col1, col2, col3 = st.columns(3)
    col1.metric("買入總成本", f"{total_cost:,} 元")
    col2.metric("損益平衡價", f"{final_be_p:.2f}")
    col3.metric("每跳一檔獲利", f"{int(tick * qty * 1000):,} 元")

    # 5. 水溫計表格
    results = []
    for i in range(5, -6, -1):
        s_p = buy_p + (i * tick)
        s_total = s_p * qty * 1000
        s_fee = int(s_total * 0.001425 * disc)
        tax = int(s_total * 0.0015)
        net = int(s_total - s_fee - tax - total_cost)
        label = f"🔺 漲 {i} 檔" if i > 0 else (f"🔻 跌 {abs(i)} 檔" if i < 0 else "🎯 買入原價")
        pct = (net / total_cost) * 100
        results.append({"市場變動": label, "建議賣出價": f"{s_p:.2f}", "實際淨損益": f"{net:,} 元", "報酬率 (%)": f"{pct:.2f}%"})

    st.table(results)
else:
    st.info("請於左側輸入買入價，系統將為您分析風險。")
