"""
Migration: Add error_message column to streams table
"""
import sqlite3
import os

def migrate():
    """Add error_message column to streams table"""
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
        
        if 'error_message' in columns:
            print("Column 'error_message' already exists in streams table")
            return True
        
        # Add the column
        print("Adding 'error_message' column to streams table...")
        cursor.execute("""
            ALTER TABLE streams 
            ADD COLUMN error_message TEXT
        """)
        
        conn.commit()
        print("Successfully added error_message column to streams table")
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

