import os
from app import create_app, db
from app.models import LearningNote

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, LearningNote=LearningNote)

def init_db_if_needed():
    with app.app_context():
        # This is a simple check. For more complex scenarios, you might need migrations.
        inspector = db.inspect(db.engine)
        if not inspector.has_table(LearningNote.__tablename__):
            db.create_all()
            # Add initial data if needed
            if LearningNote.query.count() == 0:
                initial_note = LearningNote(
                    title='碳盤查架構分析',
                    category='基礎知識',
                    content='''# 碳盤查架構概述

碳盤查架構主要建立在**溫室氣體盤查標準**之上，最廣泛採用的是國際標準ISO 14064-1和GHG Protocol企業標準。

## 核心架構組成

### 1. 盤查邊界設定
**組織邊界**：
- 營運控制權法：企業對其有營運控制權的設施進行盤查
- 財務控制權法：依據財務控制權決定盤查範圍
- 權益比例法：按持股比例分攤排放量

**營運邊界**：
- 範疇一（直接排放）：企業直接擁有或控制的排放源
- 範疇二（間接排放）：購買電力、蒸汽、熱能或冷卻所產生的間接排放
- 範疇三（其他間接排放）：價值鏈上下游的間接排放

### 2. 數據收集與計算
**活動數據收集**：
- 燃料消耗量（天然氣、柴油、汽油等）
- 電力使用量
- 製程排放數據
- 運輸數據
- 廢棄物處理數據

**排放係數應用**：
- 使用官方認可的排放係數
- 地區性電力排放係數
- 燃料特定排放係數

### 3. 品質管理系統
**數據品質確保**：
- 數據準確性驗證
- 完整性檢查
- 一致性確認
- 透明度要求

**文件管理**：
- 盤查報告書編制
- 支持文件建檔
- 版本控制管理

## 實施流程架構

### 階段一：準備階段
- 建立盤查小組
- 確定盤查目標與範圍
- 建立盤查計畫

### 階段二：執行階段
- 邊界設定與確認
- 數據收集與整理
- 排放量計算
- 不確定性分析

### 階段三：報告階段
- 盤查報告書編制
- 內部審查
- 外部查驗（如需要）

### 階段四：持續改善
- 結果分析與檢討
- 改善機會識別
- 下期盤查規劃

## 技術架構支援

### 資訊系統整合
- 碳管理平台建置
- ERP系統整合
- 自動化數據收集
- 即時監控系統

### 組織架構配置
- 高階管理層承諾
- 跨部門協調機制
- 專責人員配置
- 外部顧問支援

## 法規遵循架構

### 國際標準對接
- ISO 14064-1標準
- GHG Protocol標準
- 各國碳管制法規

### 查驗認證機制
- 第三方查驗
- 認證機構選擇
- 查驗範圍確定
- 證書管理''',
                    tags='碳盤查,架構,基礎,ISO14064,GHG Protocol'
                )
                db.session.add(initial_note)
                db.session.commit()
                print("Initial data has been added to the database.")

if __name__ == '__main__':
    init_db_if_needed()
    app.run(debug=True)
