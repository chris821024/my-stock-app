import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. 網頁基本設定
st.set_page_config(page_title="Chris | 當沖戰報", layout="centered")

# 2. CSS 優化 (移除不必要的 API 調用，專注於渲染)
st.markdown("<style>.block-container { padding-top: 1.5rem; } h1 { font-size: 22px !important; }</style>", unsafe_allow_html=True)

# 3. 全台股名單數據庫 (這裡示範核心結構，你可以無限延伸)
@st.cache_resource
def load_all_stocks():
    # 這是一個大字典，包含上市櫃絕大多數標的
    # 格式為 "代號": "名稱"
    stocks = {
        "2330":"台積電","2317":"鴻海","2454":"聯發科","2303":"聯電","2485":"兆赫",
        "2603":"長榮","2609":"陽明","2615":"萬海","2618":"長榮航","2610":"華航",
        "3231":"緯創","2382":"廣達","2376":"技嘉","2356":"英業達","1513":"中興電",
        "1519":"華城","1504":"東元","1605":"華新","2409":"友達","3481":"群創",
        "8046":"南電","3037":"欣興","3189":"景碩","2368":"金像電","2313":"華通",
        "6239":"力成","2337":"旺宏","2344":"華邦電","2408":"南亞科","3034":"聯詠",
        "1514":"亞力","1608":"華榮","1609":"大亞","6806":"森崴能源","1101":"台泥",
        "2881":"富邦金","2882":"國泰金","2891":"中信金","2886":"兆豐金","2884":"玉山金",
        # ... 這裡我預留空間，你可以把剩下的代號貼進來，或者告訴我你需要哪些產業
    }
    # 補充：如果名單真的多到數千行，我會建議你存成另一個 stocks.py 再 import
    return stocks

# 4. 損益計算邏輯
def get_tick(p):
    if p < 10: return 0.01
    elif p < 50: return 0.05
    elif p < 100: return 0.1
    elif p < 500: return 0.5
    elif p < 1000: return 1.0
    else: return 5.0

# 5. 分頁導覽
page = st.sidebar.radio("功能", ["📊 即時精算", "📝 交易日誌"])

if page == "📊 即時精算":
    components.html("<script>window.parent.document.querySelectorAll('input[type=\"number\"]')[0].focus();</script>", height=0)
    st.title("🎯 Chris | 即時損益精算")
    p1, p2 = st.columns(2)
    with p1: b_p = st.number_input("買入價格", value=None, step=0.05)
    with p2: b_q = st.number_input("購買張數", value=1, step=1)
    if b_p:
        if 'd' not in st.session_state: st.session_state.d = 0.28
        disc = st.slider(f"手續費 {st.session_state.d*10:.1f} 折", 0.1, 1.0, 0.28)
        st.session_state.d = disc
        cost = int(b_p * b_q * 1000 * (1 + 0.001425 * disc))
        st.metric("買入總成本", f"{cost:,} 元")

elif page == "📝 交易日誌":
    st.title("📈 Chris | 當沖交易戰報")
    if 'logs' not in st.session_state: st.session_state.logs = []
    
    stock_db = load_all_stocks()

    with st.expander("➕ 新增交易", expanded=True):
        c1, c2, c3 = st.columns([1,1,1])
        with c1: sym = st.text_input("股票代號")
        with c2: lp = st.number_input("買入價", min_value=0.0, step=0.05, key="lp")
        with c3: ls = st.number_input("賣出價", min_value=0.0, step=0.05, key="ls")
        
        # 這裡從內建名單抓，絕對是瞬間出結果
        found_name = stock_db.get(sym, "")
        final_name = st.text_input("股票名稱 (查無或需修正請手動填寫)", value=found_name)

        if st.button("✅ 儲存此筆戰報"):
            if not final_name and sym: final_name = sym # 如果沒名字就用代號
            d = st.session_state.get('d', 0.28)
            bc = (lp * 1000) + int(lp * 1000 * 0.001425 * d)
            sr = (ls * 1000) - int(ls * 1000 * 0.001425 * d) - int(ls * 1000 * 0.0015)
            st.session_state.logs.append({
                "代號": sym, "名稱": final_name, "損益": int(sr - bc)
            })
            st.rerun()

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.divider()
        st.metric("今日總盈虧", f"{df['損益'].sum():,} 元", delta=f"{df['損益'].sum()}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("🗑️ 清空今日紀錄"):
            st.session_state.logs = []; st.rerun()
