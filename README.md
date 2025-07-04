# 學習筆記系統 (Learning Notes System)

這是一個使用 Flask 開發的線上筆記與知識管理系統，用於建立、儲存和管理學習筆記。

## 主要功能

*   **筆記管理**: 新增、編輯、檢視和刪除筆記。
*   **所見即所得編輯器**: 使用 Quill.js 提供豐富的文字編輯功能。
*   **標籤系統**: 使用 Tagify 為每篇筆記加上多個標籤，方便分類與搜尋。
*   **程式碼高亮**: 支援在筆記中插入程式碼區塊，並使用 Prism.js 自動高亮語法。
*   **分類系統**: 每篇筆記可歸類於不同分類下。
*   **響應式設計**: 基於 Bootstrap，可在不同尺寸的裝置上正常瀏覽。

## 安裝與啟動

請依照以下步驟來設定與執行此專案：

1.  **複製專案**
    ```bash
    git clone <your-repository-url>
    cd study_web
    ```

2.  **建立並啟用虛擬環境**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安裝依賴套件**
    ```bash
    pip install -r requirements.txt
    ```

4.  **設定環境變數**
    專案使用 `config.py` 來管理設定。預設使用 `default` 設定。

5.  **初始化資料庫**
    第一次執行時，需要初始化資料庫並建立資料表。
    ```bash
    flask init_db
    ```
    此指令會建立資料庫檔案並加入一筆範例資料。

6.  **啟動應用程式**
    ```bash
    python run.py
    ```
    應用程式將會在本機的 `http://127.0.0.1:5000` 上執行。

## 主要技術棧

*   **後端**:
    *   Flask
    *   Flask-SQLAlchemy
*   **前端**:
    *   Bootstrap
    *   Quill.js (所見即所得編輯器)
    *   Tagify (標籤輸入)
    *   Prism.js (程式碼語法高亮)
*   **資產管理**:
    *   Flask-Assets

