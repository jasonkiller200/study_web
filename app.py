from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

NOTES_PER_PAGE = 9 # 每頁顯示的筆記數量

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carbon_learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 資料庫模型
class LearningNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LearningNote {self.title}>'

# 路由
@app.route('/')
def index():
    """首頁 - 顯示所有學習筆記"""
    notes = LearningNote.query.order_by(LearningNote.updated_at.desc()).all()
    categories = db.session.query(LearningNote.category).distinct().all()
    categories = [cat[0] for cat in categories]
    return render_template('index.html', notes=notes, categories=categories)

@app.route('/category/<category_name>')
def category_view(category_name):
    """按類別檢視學習筆記"""
    page = request.args.get('page', 1, type=int)
    pagination = LearningNote.query.filter_by(category=category_name).order_by(LearningNote.updated_at.desc()).paginate(
        page=page, per_page=NOTES_PER_PAGE, error_out=False
    )
    notes = pagination.items
    categories = db.session.query(LearningNote.category).distinct().all()
    categories = [cat[0] for cat in categories]
    return render_template('index.html', notes=notes, categories=categories, current_category=category_name, pagination=pagination)

@app.route('/add', methods=['GET', 'POST'])
def add_note():
    """新增學習筆記"""
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        tags = request.form['tags']
        
        note = LearningNote(
            title=title,
            category=category,
            content=content,
            tags=tags
        )
        
        db.session.add(note)
        db.session.commit()
        flash('學習筆記已成功新增！', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_note.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    """編輯學習筆記"""
    note = LearningNote.query.get_or_404(id)
    
    if request.method == 'POST':
        note.title = request.form['title']
        note.category = request.form['category']
        note.content = request.form['content']
        note.tags = request.form['tags']
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('學習筆記已成功更新！', 'success')
        return redirect(url_for('view_note', id=id))
    
    return render_template('edit_note.html', note=note)

@app.route('/view/<int:id>')
def view_note(id):
    """檢視單一學習筆記"""
    note = LearningNote.query.get_or_404(id)
    return render_template('view_note.html', note=note)

@app.route('/delete/<int:id>')
def delete_note(id):
    """刪除學習筆記"""
    note = LearningNote.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('學習筆記已成功刪除！', 'success')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    """搜尋學習筆記"""
    query = request.args.get('q', '')
    if query:
        notes = LearningNote.query.filter(
            LearningNote.title.contains(query) | 
            LearningNote.content.contains(query) |
            LearningNote.tags.contains(query)
        ).order_by(LearningNote.updated_at.desc()).all()
    else:
        notes = []
    
    categories = db.session.query(LearningNote.category).distinct().all()
    categories = [cat[0] for cat in categories]
    return render_template('index.html', notes=notes, categories=categories, search_query=query)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 生成唯一檔名
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        
        if not app.static_folder:
            return jsonify({'error': 'Static folder is not configured.'}), 500

        upload_folder = os.path.join(app.static_folder, 'images')
        os.makedirs(upload_folder, exist_ok=True)
        
        try:
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)
            location = url_for('static', filename=f'images/{unique_filename}', _external=True)
            return jsonify({'location': location})
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/notes')
def api_notes():
    """API端點 - 獲取所有筆記"""
    notes = LearningNote.query.all()
    return jsonify([{
        'id': note.id,
        'title': note.title,
        'category': note.category,
        'content': note.content,
        'tags': note.tags,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    } for note in notes])

def init_db():
    """初始化資料庫並添加初始數據"""
    with app.app_context():
        db.create_all()
        
        # 檢查是否已有數據
        if LearningNote.query.count() == 0:
            # 添加初始的碳盤查架構筆記
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
            print("初始數據已添加到資料庫")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)