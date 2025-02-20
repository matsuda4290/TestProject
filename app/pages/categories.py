import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

def load_categories():
    """カテゴリデータの読み込み"""
    conn = sqlite3.connect('data/finance.db')
    
    # カテゴリ一覧の取得（使用状況も含む）
    categories_df = pd.read_sql("""
        SELECT 
            c.*,
            COALESCE(SUM(t.amount), 0) as current_month_amount,
            COUNT(t.id) as transaction_count
        FROM categories c
        LEFT JOIN transactions t ON 
            c.id = t.category_id AND 
            strftime('%Y-%m', t.date) = strftime('%Y-%m', 'now')
        GROUP BY c.id
        ORDER BY c.type, c.sort_order
    """, conn)
    
    conn.close()
    return categories_df

def update_category(category_id, name, budget=None):
    """カテゴリの更新"""
    conn = sqlite3.connect('data/finance.db')
    cursor = conn.cursor()
    
    if budget is not None:
        cursor.execute("""
            UPDATE categories 
            SET name = ?, budget = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (name, budget, category_id))
    else:
        cursor.execute("""
            UPDATE categories 
            SET name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (name, category_id))
    
    conn.commit()
    conn.close()

def add_category(name, category_type, budget=None):
    """新規カテゴリの追加"""
    conn = sqlite3.connect('data/finance.db')
    cursor = conn.cursor()
    
    # 同じtype内での最大sort_orderを取得
    cursor.execute("""
        SELECT MAX(sort_order) FROM categories WHERE type = ?
    """, (category_type,))
    max_order = cursor.fetchone()[0] or -1
    
    cursor.execute("""
        INSERT INTO categories (name, type, sort_order, budget)
        VALUES (?, ?, ?, ?)
    """, (name, category_type, max_order + 1, budget))
    
    conn.commit()
    conn.close()

def toggle_category_status(category_id, is_active):
    """カテゴリの有効/無効を切り替え"""
    conn = sqlite3.connect('data/finance.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE categories 
        SET is_active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (is_active, category_id))
    
    conn.commit()
    conn.close()

def main():
    st.title("📑 カテゴリ管理")
    
    # カテゴリデータの読み込み
    categories_df = load_categories()
    
    # 新規カテゴリ追加フォーム
    st.header("新規カテゴリの追加")
    with st.form("add_category_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_category_name = st.text_input("カテゴリ名", max_chars=50)
        with col2:
            category_type = st.selectbox("種別", ["expense", "income"], format_func=lambda x: "支出" if x == "expense" else "収入")
        with col3:
            budget = st.number_input("月次予算 (支出の場合)", min_value=0, step=1000) if category_type == "expense" else None
        
        submit_button = st.form_submit_button("カテゴリを追加")
        if submit_button and new_category_name:
            # 重複チェック
            if not categories_df[
                (categories_df["type"] == category_type) & 
                (categories_df["name"] == new_category_name)
            ].empty:
                st.error("同じ種別で既に同名のカテゴリが存在します。")
            else:
                add_category(new_category_name, category_type, budget)
                st.success("カテゴリを追加しました！")
                st.rerun()
    
    # カテゴリ一覧表示
    tab1, tab2 = st.tabs(["支出カテゴリ", "収入カテゴリ"])
    
    # 支出カテゴリタブ
    with tab1:
        expense_df = categories_df[categories_df["type"] == "expense"].copy()
        for _, row in expense_df.iterrows():
            with st.expander(f"{'🟢' if row['is_active'] else '⚫'} {row['name']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_name = st.text_input("カテゴリ名", row["name"], key=f"name_{row['id']}")
                with col2:
                    new_budget = st.number_input("月次予算", value=row["budget"] or 0, key=f"budget_{row['id']}")
                with col3:
                    st.metric("当月利用額", f"¥{row['current_month_amount']:,.0f}")
                    if row["budget"]:
                        progress = min(100, (row["current_month_amount"] / row["budget"]) * 100)
                        st.progress(progress / 100, text=f"予算達成率: {progress:.1f}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("更新", key=f"update_{row['id']}"):
                        update_category(row["id"], new_name, new_budget)
                        st.success("更新しました！")
                        st.rerun()
                with col2:
                    if row["transaction_count"] == 0:
                        if st.button(
                            "無効化" if row["is_active"] else "有効化", 
                            key=f"toggle_{row['id']}"
                        ):
                            toggle_category_status(row["id"], not row["is_active"])
                            st.success("ステータスを更新しました！")
                            st.rerun()
    
    # 収入カテゴリタブ
    with tab2:
        income_df = categories_df[categories_df["type"] == "income"].copy()
        for _, row in income_df.iterrows():
            with st.expander(f"{'🟢' if row['is_active'] else '⚫'} {row['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("カテゴリ名", row["name"], key=f"name_{row['id']}")
                with col2:
                    st.metric("当月金額", f"¥{row['current_month_amount']:,.0f}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("更新", key=f"update_{row['id']}"):
                        update_category(row["id"], new_name)
                        st.success("更新しました！")
                        st.rerun()
                with col2:
                    if row["transaction_count"] == 0:
                        if st.button(
                            "無効化" if row["is_active"] else "有効化", 
                            key=f"toggle_{row['id']}"
                        ):
                            toggle_category_status(row["id"], not row["is_active"])
                            st.success("ステータスを更新しました！")
                            st.rerun()

if __name__ == "__main__":
    main()
