import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, date
import os

def load_assets_data():
    """資産データの読み込み"""
    conn = sqlite3.connect('data/finance.db')
    
    # 資産推移データの取得
    assets_df = pd.read_sql("""
        SELECT date, balance
        FROM assets
        ORDER BY date
    """, conn)
    
    # 月次収支データの取得
    monthly_balance_df = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
        FROM transactions
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """, conn)
    
    conn.close()
    return assets_df, monthly_balance_df

def update_asset_balance(date_val, balance):
    """資産残高の更新"""
    conn = sqlite3.connect('data/finance.db')
    cursor = conn.cursor()
    
    # 同じ日付の残高が存在する場合は更新、なければ挿入
    cursor.execute("""
        INSERT OR REPLACE INTO assets (date, balance)
        VALUES (?, ?)
    """, (date_val, balance))
    
    conn.commit()
    conn.close()

def main():
    st.title("💰 資産管理")
    
    # 資産残高の入力セクション
    st.header("資産残高の登録・更新")
    col1, col2 = st.columns(2)
    with col1:
        date_val = st.date_input("日付", value=date.today())
    with col2:
        balance = st.number_input("残高 (円)", min_value=0, step=1000)
    
    if st.button("残高を登録"):
        update_asset_balance(date_val, balance)
        st.success("残高を更新しました！")
    
    # 資産データの読み込み
    assets_df, monthly_balance_df = load_assets_data()
    
    # 資産推移グラフの表示
    if not assets_df.empty:
        st.header("資産推移")
        fig = px.line(
            assets_df,
            x="date",
            y="balance",
            title="資産残高の推移",
            labels={"date": "日付", "balance": "残高 (円)"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 現在の資産残高表示
        latest_balance = assets_df.iloc[-1]["balance"]
        st.metric(
            label="現在の資産残高",
            value=f"¥{latest_balance:,.0f}",
            delta=f"¥{assets_df.iloc[-1]['balance'] - assets_df.iloc[0]['balance']:,.0f}"
        )
    
    # 月次収支バランスの表示
    if not monthly_balance_df.empty:
        st.header("月次収支バランス")
        monthly_balance_df["balance"] = monthly_balance_df["income"] - monthly_balance_df["expense"]
        
        # データフレームの表示形式を整える
        display_df = monthly_balance_df.copy()
        display_df = display_df.rename(columns={
            "month": "年月",
            "income": "収入",
            "expense": "支出",
            "balance": "収支"
        })
        
        # 金額を通貨形式で表示
        for col in ["収入", "支出", "収支"]:
            display_df[col] = display_df[col].apply(lambda x: f"¥{x:,.0f}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    main()
