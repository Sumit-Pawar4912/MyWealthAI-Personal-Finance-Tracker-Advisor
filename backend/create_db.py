#!/usr/bin/env python
"""
Database initialization script
Run this script to create the database tables
"""

from app import app
from app.database import db
from app.models import User, Transaction

def create_database():
    """Create all database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("[OK] Database created successfully!")
        print("Database location: instance/mywelthai.db")
        
        # Check tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nTables created: {', '.join(tables)}")

if __name__ == '__main__':
    create_database()




