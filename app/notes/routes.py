from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from . import notes
from .. import db
from ..models import LearningNote
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
        return redirect(url_for('main.index'))
    
    return render_template('add_note.html')

@notes.route('/<int:id>')
def view_note(id):
    note = LearningNote.query.get_or_404(id)
    processed_tags = []
    if note.tags:
        try:
            tags_list = json.loads(note.tags)
            if isinstance(tags_list, list) and all(isinstance(tag, dict) and 'value' in tag for tag in tags_list):
                processed_tags = [tag['value'] for tag in tags_list]
            else:
                processed_tags = [tag.strip() for tag in note.tags.split(',')]
        except json.JSONDecodeError:
            processed_tags = [tag.strip() for tag in note.tags.split(',')]

    return render_template('view_note.html', note=note, processed_tags=processed_tags)

@notes.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_note(id):
    note = LearningNote.query.get_or_404(id)
    
    if request.method == 'POST':
        note.title = request.form['title']
        note.category = request.form['category']
        note.content = request.form['content']
        note.tags = request.form['tags']
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('學習筆記已成功更新！', 'success')
        return redirect(url_for('.view_note', id=id))
    
    return render_template('edit_note.html', note=note)

@notes.route('/<int:id>/delete')
def delete_note(id):
    note = LearningNote.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('學習筆記已成功刪除！', 'success')
    return redirect(url_for('main.index'))

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
        
        # This needs to be adapted to the app factory pattern
        # For now, we assume the static folder is in the app root
        upload_folder = os.path.join(current_app.static_folder, 'images')
        os.makedirs(upload_folder, exist_ok=True)
        
        try:
            filepath = os.path.join(upload_folder, unique_filename)
            # Image processing with Pillow
            img = Image.open(file.stream)
            
            # Resize if larger than MAX_IMAGE_WIDTH
            if img.width > current_app.config['MAX_IMAGE_WIDTH']:
                width_percent = (current_app.config['MAX_IMAGE_WIDTH'] / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(width_percent)))
                img = img.resize((current_app.config['MAX_IMAGE_WIDTH'], hsize), Image.LANCZOS)
            
            # Save with specified quality
            img.save(filepath, quality=current_app.config['IMAGE_QUALITY'])
            location = url_for('static', filename=f'images/{unique_filename}', _external=True)
            return jsonify({'location': location})
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400