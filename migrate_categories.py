import os
from app import create_app, db
from app.models import LearningNote, Category
import sqlalchemy as sa

def run_migration():
    """
    One-time script to migrate from a string-based 'category' field
    to a foreign key-based 'category_id' field.
    """
    print("--- Starting Category Data Migration ---")
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        engine = db.get_engine()
        
        # Step 1: Check if migration is necessary by looking for the old 'category' column.
        try:
            with engine.connect() as connection:
                # This will fail if the column does not exist.
                connection.execute(sa.text('SELECT category FROM learning_note LIMIT 1'))
            print("Old 'category' column found. Proceeding with migration.")
        except Exception:
            print(f"Could not find the old 'category' column. It's likely the migration has already been run or is not needed.")
            # Ensure new tables/columns exist anyway
            print("Ensuring all tables are created according to current models...")
            db.create_all()
            print("--- Migration Finished (or was not needed) ---")
            return

        # Step 2: Ensure the new Category table exists.
        print("Creating new tables (if they don't exist)...")
        db.create_all()

        # Step 2.5: Manually add the 'category_id' column to 'learning_note' as db.create_all() won't alter existing tables.
        print("Attempting to add 'category_id' column to 'learning_note' table...")
        try:
            with engine.connect() as connection:
                connection.execute(sa.text('ALTER TABLE learning_note ADD COLUMN category_id INTEGER'))
                # For some DBs, ALTER TABLE in a transaction needs a commit.
                # For SQLite, it's often autocommitted, but explicit is safer.
                if connection.in_transaction():
                    connection.commit()
            print("'category_id' column added successfully.")
        except Exception as e:
            # This will likely fail if the column already exists, which is fine.
            print(f"Could not add column, probably because it already exists. (Error: {e})")


        # Step 3: Use raw SQL to fetch old data (id, category name).
        notes_to_migrate = []
        with engine.connect() as connection:
            result = connection.execute(sa.text('SELECT id, category FROM learning_note'))
            notes_to_migrate = result.fetchall()
        
        if not notes_to_migrate:
            print("No notes found to migrate.")
        else:
            print(f"Found {len(notes_to_migrate)} note entries to process.")
        
            # Step 4: Find unique category names, create Category objects, and save them.
            old_category_names = sorted(list(set(row[1] for row in notes_to_migrate if row[1])))
            print(f"Found {len(old_category_names)} unique category names: {old_category_names}")
            
            category_map = {}  # Maps name to its new ID
            for name in old_category_names:
                category = Category.query.filter_by(name=name).first()
                if not category:
                    category = Category(name=name)
                    db.session.add(category)
            
            print("Committing new categories to the database...")
            db.session.commit()
            print("Categories committed.")

            # Build the name -> id map after committing
            for name in old_category_names:
                category = Category.query.filter_by(name=name).first()
                category_map[name] = category.id
            
            # Step 5: Update each note with the correct category_id.
            print("Updating learning notes with new foreign keys...")
            for note_id, old_cat_name in notes_to_migrate:
                if old_cat_name in category_map:
                    note = LearningNote.query.get(note_id)
                    if note:
                        note.category_id = category_map[old_cat_name]
                else:
                    print(f"Warning: Note ID {note_id} had an empty or unmapped category '{old_cat_name}'.")

            print("Committing updated notes...")
            db.session.commit()
            print("Notes updated.")

        print("\n--- MIGRATION COMPLETE ---")
        print("Data has been migrated to the new Category model.")
        print("IMPORTANT: The old 'category' column has NOT been deleted from the 'learning_note' table.")
        print("You can manually delete it later using a database tool if you wish.")


if __name__ == '__main__':
    run_migration()
