from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from . import notes
from .. import db
from ..models import LearningNote, Category
from datetime import datetime
import json
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image


def allowed_file(filename):
    return '.' in filename and            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@notes.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id', type=int)
        content = request.form.get('content')
        tags = request.form.get('tags')

        if not all([title, category_id, content]):
            flash('標題、分類和內容為必填欄位。', 'danger')
            # Repopulate categories for the template
            categories = Category.query.order_by(Category.name).all()
            return render_template('add_note.html', categories=categories, note=request.form), 400

        note = LearningNote(
            title=title,
            category_id=category_id,
            content=content,
            tags=tags
        )
        
        db.session.add(note)
        db.session.commit()
        flash('學習筆記已成功新增！', 'success')
        return redirect(url_for('main.index'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('add_note.html', categories=categories)

@notes.route('/<int:id>')
def view_note(id):
    note = LearningNote.query.get_or_404(id)
    return render_template('view_note.html', note=note)

@notes.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_note(id):
    note = LearningNote.query.get_or_404(id)
    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id', type=int)
        content = request.form.get('content')

        if not all([title, category_id, content]):
            flash('標題、分類和內容為必填欄位。', 'danger')
            categories = Category.query.order_by(Category.name).all()
            # Pass the current note object so the form can be repopulated
            return render_template('edit_note.html', note=note, categories=categories), 400

        note.title = title
        note.category_id = category_id
        note.content = request.form['content']
        note.tags = request.form['tags']
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('學習筆記已成功更新！', 'success')
        return redirect(url_for('.view_note', id=id))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('edit_note.html', note=note, categories=categories)

@notes.route('/<int:id>/delete')
def delete_note(id):
    note = LearningNote.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('學習筆記已成功刪除！', 'success')
    return redirect(url_for('main.index'))

@notes.route('/api/add_category', methods=['POST'])
def add_category():
    data = request.get_json()
    if not data or 'name' not in data or not data['name'].strip():
        return jsonify({'error': 'Category name is required.'}), 400
    
    name = data['name'].strip()
    
    existing_category = Category.query.filter(Category.name.ilike(name)).first()
    if existing_category:
        # Return the existing category's data
        return jsonify({
            'id': existing_category.id, 
            'name': existing_category.name,
            'existed': True
        }), 200

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify({
        'id': new_category.id, 
        'name': new_category.name
    }), 201


@notes.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        
        upload_folder = os.path.join(current_app.static_folder, 'images')
        os.makedirs(upload_folder, exist_ok=True)
        
        try:
            filepath = os.path.join(upload_folder, unique_filename)
            img = Image.open(file.stream)
            
            if img.width > current_app.config['MAX_IMAGE_WIDTH']:
                width_percent = (current_app.config['MAX_IMAGE_WIDTH'] / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(width_percent)))
                img = img.resize((current_app.config['MAX_IMAGE_WIDTH'], hsize), Image.LANCZOS)
            
            img.save(filepath, quality=current_app.config['IMAGE_QUALITY'])
            location = url_for('static', filename=f'images/{unique_filename}', _external=True)
            return jsonify({'location': location})
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400
