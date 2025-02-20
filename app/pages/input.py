import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

def load_categories():
    """有効なカテゴリの読み込み"""
    conn = sqlite3.connect('data/finance.db')
    categories_df = pd.read_sql("""
        SELECT id, name, type
        FROM categories
        WHERE is_active = 1
        ORDER BY type, sort_order
    """, conn)
    conn.close()
    return categories_df

def save_transaction(date_val, amount, transaction_type, category_id, memo):
    """取引データの保存"""
    conn = sqlite3.connect('data/finance.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO transactions (date, amount, type, category_id, memo)
        VALUES (?, ?, ?, ?, ?)
    """, (date_val, amount, transaction_type, category_id, memo))
    
    conn.commit()
    conn.close()

def main():
    st.title("💸 収支入力")
    
    # カテゴリデータの読み込み
    categories_df = load_categories()
    
    # 入力フォーム
    with st.form("transaction_form"):
        # 日付入力
        date_val = st.date_input("日付", value=date.today())
        
        # 金額入力
        amount = st.number_input("金額", min_value=0, step=100)
        
        # 収支区分選択
        transaction_type = st.selectbox(
            "収支区分",
            ["expense", "income"],
            format_func=lambda x: "支出" if x == "expense" else "収入"
        )
        
        # カテゴリ選択
        filtered_categories = categories_df[categories_df["type"] == transaction_type]
        category_id = st.selectbox(
            "カテゴリ",
            filtered_categories["id"].tolist(),
            format_func=lambda x: filtered_categories[filtered_categories["id"] == x]["name"].iloc[0]
        )
        
        # メモ入力
        memo = st.text_input("メモ（任意）", max_chars=200)
        
        # 送信ボタン
        submitted = st.form_submit_button("登録")
        
        if submitted:
            if amount > 0:
                save_transaction(date_val, amount, transaction_type, category_id, memo)
                st.success("登録が完了しました！")
                
                # 登録後の処理
                if transaction_type == "expense":
                    message = f"支出 ¥{amount:,} を {filtered_categories[filtered_categories['id'] == category_id]['name'].iloc[0]} として記録しました。"
                else:
                    message = f"収入 ¥{amount:,} を {filtered_categories[filtered_categories['id'] == category_id]['name'].iloc[0]} として記録しました。"
                st.info(message)
            else:
                st.error("金額を入力してください。")

    # 最近の取引履歴を表示
    st.header("最近の取引")
    conn = sqlite3.connect('data/finance.db')
    recent_transactions = pd.read_sql("""
        SELECT 
            t.date,
            t.amount,
            t.type,
            c.name as category,
            t.memo
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        ORDER BY t.created_at DESC
        LIMIT 5
    """, conn)
    conn.close()
    
    if not recent_transactions.empty:
        for _, tx in recent_transactions.iterrows():
            with st.expander(
                f"{'🔴' if tx['type'] == 'expense' else '🟢'} "
                f"{tx['date']} - ¥{tx['amount']:,} ({tx['category']})"
            ):
                if tx['memo']:
                    st.write(f"メモ: {tx['memo']}")

if __name__ == "__main__":
    main()
