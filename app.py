# ... (前面代碼保持不變) ...

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
            buy_price = st.number_input("買入價", min_value=0.0, step=0.05, key="log_buy")
        with c3:
            sell_price = st.number_input("賣出價", min_value=0.0, step=0.05, key="log_sell")
        
        c4, c5 = st.columns(2)
        with c4:
            log_qty = st.number_input("張數", min_value=1, step=1, key="log_qty")
        with c5:
            stock_name = "等待輸入..."
            if symbol:
                # 強化搜尋邏輯：優先嘗試 .TW，失敗則嘗試 .TWO
                try:
                    t = yf.Ticker(f"{symbol}.TW")
                    stock_name = t.info.get('longName') or t.info.get('shortName')
                    if not stock_name: # 如果還是空的，試試看上櫃後綴
                        t = yf.Ticker(f"{symbol}.TWO")
                        stock_name = t.info.get('longName') or t.info.get('shortName')
                except:
                    stock_name = "查無此代號"
                
                if not stock_name: stock_name = "搜尋中..."
            st.write(f"股票名稱：**{stock_name}**")

# ... (後續紀錄與顯示邏輯保持不變) ...
