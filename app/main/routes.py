from flask import render_template, request, current_app, session, jsonify, flash, redirect, url_for
from . import main
from .. import db
from ..models import LearningNote, Category

@main.app_context_processor
def inject_categories():
    """Injects categories into all templates."""
    try:
        categories = Category.query.order_by(Category.name).all()
        return dict(categories=categories)
    except Exception:
        # Return an empty list if the database isn't set up yet
        return dict(categories=[])

@main.route('/')
def index():
    NOTES_PER_PAGE = current_app.config['NOTES_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = LearningNote.query.order_by(LearningNote.updated_at.desc()).paginate(
        page=page, per_page=NOTES_PER_PAGE, error_out=False
    )
    notes = pagination.items

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('_note_cards.html', notes=notes)

    return render_template('index.html', notes=notes, pagination=pagination)

@main.route('/search')
def search():
    NOTES_PER_PAGE = current_app.config['NOTES_PER_PAGE']
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    if query:
        search_query = LearningNote.query.filter(
            LearningNote.title.ilike(f'%{query}%') |
            LearningNote.content.ilike(f'%{query}%') |
            LearningNote.tags.ilike(f'%{query}%')
        ).order_by(LearningNote.updated_at.desc())
        
        pagination = search_query.paginate(
            page=page, per_page=NOTES_PER_PAGE, error_out=False
        )
        notes = pagination.items
    else:
        notes = []
        pagination = None

    return render_template('index.html', notes=notes, search_query=query, pagination=pagination)

@main.route('/category/<category_name>')
def category_view(category_name):
    NOTES_PER_PAGE = current_app.config['NOTES_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    
    # Query using the relationship
    category = Category.query.filter_by(name=category_name).first_or_404()
    pagination = LearningNote.query.with_parent(category).order_by(LearningNote.updated_at.desc()).paginate(
        page=page, per_page=NOTES_PER_PAGE, error_out=False
    )
    
    notes = pagination.items
    return render_template('index.html', notes=notes, current_category=category_name, pagination=pagination)

@main.route('/check_admin', methods=['POST'])
def check_admin():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'success': False, 'message': '未提供密碼。'}), 400

    password = data.get('password')
    if password == current_app.config['ADMIN_PASSWORD']:
        session['is_admin'] = True
        return jsonify({'success': True})
    else:
        session.pop('is_admin', None)
        return jsonify({'success': False, 'message': '管理員密碼錯誤。'}), 401

@main.route('/admin_logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('您已登出管理員模式。', 'info')
    return redirect(url_for('main.index'))
