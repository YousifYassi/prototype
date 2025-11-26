"""
Migration: Add browser_preview_url column to streams table
"""
import sqlite3
import os

def migrate():
    """Add browser_preview_url column to streams table"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'workplace_safety.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(streams)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'browser_preview_url' in columns:
            print("Column 'browser_preview_url' already exists in streams table")
            return True
        
        # Add the column
        print("Adding 'browser_preview_url' column to streams table...")
        cursor.execute("""
            ALTER TABLE streams 
            ADD COLUMN browser_preview_url TEXT
        """)
        
        conn.commit()
        print("Successfully added browser_preview_url column to streams table")
        print("Note: Existing streams will use source_url for both AI and browser preview (NULL = use source_url)")
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)


