#!/usr/bin/env python3
from app import app, init_db

if __name__ == '__main__':
    init_db()
    print(" 碳盤查學習心得系統啟動中...")
    print(" 網址: http://localhost:5000")
    print(" 開發模式: 已啟用")
    app.run(debug=True, host='0.0.0.0', port=5000)