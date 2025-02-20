import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# アプリケーションの設定
st.set_page_config(
    page_title="家計管理アプリ",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# データベースの初期化
def init_db():
    db_path = os.path.join('data', 'finance.db')
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # categoriesテーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            type VARCHAR(10) NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            budget DECIMAL(10,2),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # transactionsテーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            type VARCHAR(10) NOT NULL,
            category_id INTEGER NOT NULL,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    # assetsテーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            balance DECIMAL(12,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 初期カテゴリの登録（まだ存在しない場合のみ）
    expense_categories = [
        "食費", "住居費", "光熱費", "通信費", "交通費",
        "教育費", "娯楽費", "医療費", "その他"
    ]
    income_categories = ["給与", "賞与", "副収入", "その他収入"]
    
    # 支出カテゴリの登録
    for i, category in enumerate(expense_categories):
        c.execute('''
            INSERT OR IGNORE INTO categories (name, type, sort_order)
            SELECT ?, 'expense', ?
            WHERE NOT EXISTS (
                SELECT 1 FROM categories 
                WHERE name = ? AND type = 'expense'
            )
        ''', (category, i, category))
    
    # 収入カテゴリの登録
    for i, category in enumerate(income_categories):
        c.execute('''
            INSERT OR IGNORE INTO categories (name, type, sort_order)
            SELECT ?, 'income', ?
            WHERE NOT EXISTS (
                SELECT 1 FROM categories 
                WHERE name = ? AND type = 'income'
            )
        ''', (category, i, category))
    
    conn.commit()
    conn.close()

# アプリケーションの初期化
def main():
    # データベースの初期化
    init_db()
    
    # アプリケーションのタイトル
    st.title("💰 家計管理アプリ")
    
    # 今月の収支サマリーを表示
    st.header("今月の収支サマリー")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="収入", value="¥0", delta="前月比 ¥0")
    
    with col2:
        st.metric(label="支出", value="¥0", delta="前月比 ¥0")
    
    with col3:
        st.metric(label="収支バランス", value="¥0", delta="前月比 ¥0")
    
    # メインコンテンツ
    st.markdown("""
    ### 👈 サイドバーからメニューを選択してください
    
    **利用可能な機能：**
    - 収支入力
    - 収支サマリー
    - 資産管理
    - カテゴリ管理
    """)

if __name__ == "__main__":
    main()
