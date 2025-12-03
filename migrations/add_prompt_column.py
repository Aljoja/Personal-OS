"""Add start_prompt column to learning_challenges table"""

import sqlite3
from pathlib import Path

def migrate():
    """Add start_prompt column if it doesn't exist"""
    
    db_path = Path("brain/knowledge.db")
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        columns = [col[1] for col in cursor.execute("PRAGMA table_info(learning_challenges)")]
        
        if 'start_prompt' in columns:
            print("✅ Column 'start_prompt' already exists")
            return True
        
        # Add column
        cursor.execute("""
            ALTER TABLE learning_challenges 
            ADD COLUMN start_prompt TEXT
        """)
        
        conn.commit()
        print("✅ Added 'start_prompt' column to learning_challenges")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()