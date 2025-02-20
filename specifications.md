# 家計管理アプリケーション要件定義書

## 1. システム概要

### 1.1 目的
- 日々の収支を簡単に記録・管理できるWebアプリケーション
- 資産推移の可視化による家計の健全性の把握
- カテゴリ別の支出分析による家計の最適化支援
- ユーザーごとのカスタマイズ可能なカテゴリ管理

### 1.2 システム構成
- フロントエンド: Streamlit
- バックエンド: Python
- データベース: SQLite3

## 2. 機能要件

### 2.1 基本機能
1. 収支登録機能
   - 日付、金額、カテゴリ、メモの登録
   - 入金/出金の区分選択
   - 登録内容の編集・削除

2. 収支閲覧機能
   - 月別収支一覧表示
   - カテゴリ別支出集計
   - 期間指定による収支検索

3. 資産管理機能
   - 資産残高の表示
   - 資産推移グラフの表示
   - 月次収支サマリー

4. カテゴリ管理機能 【新規追加】
   - カテゴリの新規追加
   - カテゴリ名の編集
   - カテゴリの無効化（削除フラグ）
   - カテゴリの並べ替え
   - カテゴリごとの予算設定

### 2.2 カテゴリ管理
**初期支出カテゴリ**（ユーザーによる追加・編集可能）
- 食費
- 住居費
- 光熱費
- 通信費
- 交通費
- 教育費
- 娯楽費
- 医療費
- その他

**初期収入カテゴリ**（ユーザーによる追加・編集可能）
- 給与
- 賞与
- 副収入
- その他収入

## 3. 技術仕様

### 3.1 フォルダ構成
```
KAKEIBO_APP/
├── app/
│   ├── main.py          # メインアプリケーション
│   ├── pages/
│   │   ├── input.py     # 収支入力ページ
│   │   ├── summary.py   # 収支サマリーページ
│   │   ├── assets.py    # 資産管理ページ
│   │   └── categories.py # カテゴリ管理ページ 【新規追加】
│   ├── models/
│   │   ├── database.py  # データベース接続管理
│   │   └── schema.py    # データベーススキーマ定義
│   └── utils/
│       ├── constants.py  # 定数定義
│       └── helpers.py    # ユーティリティ関数
├── data/
│   └── finance.db       # SQLiteデータベース
├── tests/               # テストコード
└── requirements.txt     # 依存ライブラリ
```

### 3.2 使用ライブラリ
```
streamlit==1.32.0
pandas==2.2.0
plotly==5.18.0
sqlite3
numpy==1.26.0
```

### 3.3 データベーススキーマ

**categories テーブル**（更新）
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    type VARCHAR(10) NOT NULL,  -- 'income' or 'expense'
    sort_order INTEGER NOT NULL DEFAULT 0,  -- 表示順
    budget DECIMAL(10,2),       -- 月次予算（支出カテゴリのみ）
    is_active BOOLEAN DEFAULT 1,-- カテゴリの有効/無効状態
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**transactions テーブル**
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    type VARCHAR(10) NOT NULL,  -- 'income' or 'expense'
    category_id INTEGER NOT NULL,
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

**assets テーブル**
```sql
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    balance DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 画面仕様

### 4.1 収支入力画面
- 日付選択（デフォルトは当日）
- 金額入力フィールド
- 収支区分（入金/出金）選択
- カテゴリ選択ドロップダウン
- メモ入力フィールド（任意）
- 登録ボタン

### 4.2 収支サマリー画面
- 月次収支グラフ
- カテゴリ別支出円グラフ
- 期間指定による収支一覧表
- カテゴリ別集計表
- カテゴリ別予算達成状況

### 4.3 資産管理画面
- 現在の資産残高表示
- 資産推移折れ線グラフ
- 月次収支バランス表示

### 4.4 カテゴリ管理画面 【新規追加】
- カテゴリ一覧表示（収入・支出タブ分け）
- カテゴリ追加フォーム
  - カテゴリ名入力
  - 種別選択（収入/支出）
  - 月次予算設定（支出の場合）
  - 追加ボタン
- 各カテゴリの編集機能
  - カテゴリ名変更
  - 予算額変更
  - 表示順変更（ドラッグ&ドロップ）
  - 無効化ボタン
- カテゴリの使用状況表示
  - 当月の利用額
  - 予算達成率（支出の場合）

## 5. カテゴリ管理に関する制約 【新規追加】
- すでに取引で使用されているカテゴリは削除不可（無効化のみ可能）
- カテゴリ名は1文字以上50文字以内
- 同じ種別（収入/支出）内でカテゴリ名の重複は不可
- 予算額は0円以上
- 無効化されたカテゴリは新規取引で選択不可
- 表示順は同じ種別内で一意の値を持つ

## 6. セキュリティ要件
- SQLインジェクション対策
- 入力値のバリデーション
- エラーハンドリング

## 7. 非機能要件
- レスポンス時間：1秒以内
- 同時接続ユーザー：シングルユーザーを想定
- データバックアップ：日次