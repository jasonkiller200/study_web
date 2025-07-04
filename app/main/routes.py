from flask import render_template, request, current_app
from . import main
from .. import db
from ..models import LearningNote

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

    categories = db.session.query(LearningNote.category).distinct().all()
    categories = [cat[0] for cat in categories]
    return render_template('index.html', notes=notes, categories=categories, pagination=pagination)

@main.route('/search')
def search():
    NOTES_PER_PAGE = current_app.config['NOTES_PER_PAGE']
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int) # Add page parameter

    if query:
        # Build the query
        search_query = LearningNote.query.filter(
            LearningNote.title.ilike(f'%{query}%') |
            LearningNote.content.ilike(f'%{query}%') |
            LearningNote.tags.ilike(f'%{query}%')
        ).order_by(LearningNote.updated_at.desc())

        # Apply pagination
        pagination = search_query.paginate(
            page=page, per_page=NOTES_PER_PAGE, error_out=False
        )
        notes = pagination.items
    else:
        notes = []
        pagination = None # No pagination if no query

    categories = db.session.query(LearningNote.category).distinct().all()
    categories = [cat[0] for cat in categories]
    return render_template('index.html', notes=notes, categories=categories, search_query=query, pagination=pagination) # Pass pagination

@main.route('/category/<category_name>')
def category_view(category_name):
    NOTES_PER_PAGE = current_app.config['NOTES_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = LearningNote.query.filter_by(category=category_name).order_by(LearningNote.updated_at.desc()).paginate(
        page=page, per_page=NOTES_PER_PAGE, error_out=False
    )
    notes = pagination.items
    categories = db.session.query(LearningNote.category).distinct().all()
    categories = [cat[0] for cat in categories]
    return render_template('index.html', notes=notes, categories=categories, current_category=category_name, pagination=pagination)
