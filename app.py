import streamlit as st

# 設定網頁標題
st.title("📈 我的專屬當沖計算器")
st.write("輸入買入數據，即時查看各個 Tick 的損益。")

# 側邊欄輸入區
with st.sidebar:
    st.header("參數設定")
    buy_p = st.number_input("買入價格", value=15.6, step=0.05)
    qty = st.number_input("購買張數", value=2, step=1)
    disc = st.slider("手續費折扣", 0.1, 1.0, 0.28)

# 判斷 Tick 大小
if buy_p < 50: tick = 0.05
elif buy_p < 100: tick = 0.05
elif buy_p < 500: tick = 0.5
else: tick = 1.0

# 計算買進成本
total_cost = (buy_p * qty * 1000) + int(buy_p * qty * 1000 * 0.001425 * disc)

# 顯示結果
st.subheader(f"買入總成本：{total_cost:,} 元")

# 建立表格數據
results = []
for i in range(0, 7):
    s_p = buy_p + (i * tick)
    s_total = s_p * qty * 1000
    s_fee = int(s_total * 0.001425 * disc)
    tax = int(s_total * 0.0015) # 當沖減半
    net = int(s_total - s_fee - tax - total_cost)
    results.append({"跳動": f"跳 {i} 檔", "賣出價": s_p, "淨損益": f"{net:,} 元"})

# 輸出漂亮表格
st.table(results)

if int(results[1]["淨損益"].replace(",","").replace(" 元","")) > 0:
    st.success("✅ 這檔股票跳 1 檔就賺錢！")
else:
    st.warning("⚠️ 這檔股票需要跳更多檔才能保本。")
