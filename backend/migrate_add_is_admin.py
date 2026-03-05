"""
Migration script to add is_admin column to users table
This preserves existing user data while adding the new column
"""

import sqlite3
import os
from pathlib import Path

def migrate_add_is_admin():
    """Add is_admin column to users table if it doesn't exist"""
    
    # Database path
    db_path = Path(__file__).parent / 'instance' / 'mywelthai.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("Please run the application first to create the database")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("✅ Column 'is_admin' already exists in users table")
            conn.close()
            return True
        
        # Add the column if it doesn't exist
        print("⏳ Adding 'is_admin' column to users table...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN is_admin BOOLEAN DEFAULT 0
        """)
        
        conn.commit()
        print("✅ Successfully added 'is_admin' column to users table")
        print("✅ All existing users default to is_admin=False")
        
        # Show number of users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Total users in database: {user_count}")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        print(f"❌ SQLite Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Running migration: Add is_admin column to users table")
    print("-" * 60)
    
    success = migrate_add_is_admin()
    
    print("-" * 60)
    if success:
        print("✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Run: python run.py")
        print("   2. Visit: http://localhost:5173/login")
        print("   3. Try logging in - it should work now!")
    else:
        print("❌ Migration failed. Please check the error above.")
