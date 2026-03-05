#!/usr/bin/env python
"""
Admin Setup Script
Promotes a user to admin or creates an admin account.

Usage:
    python admin_setup.py
"""

from app import app
from app.database import db
from app.models.models import User
import sys

def admin_setup():
    """Interactive admin setup"""
    print("\n=== MyWelthAI Admin Setup ===\n")
    
    with app.app_context():
        # List existing users
        users = User.query.all()
        print(f"Total users in database: {len(users)}\n")
        
        if users:
            print("Existing users:")
            for i, u in enumerate(users, 1):
                admin_badge = " [ADMIN]" if u.is_admin else ""
                print(f"{i}. {u.email} - {u.first_name} {u.last_name}{admin_badge}")
            print()
        
        # Menu
        print("Options:")
        print("1. Promote existing user to admin")
        print("2. Create new admin account")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            if not users:
                print("No users found. Create one first via registration.\n")
                return
            
            email = input("Enter email to promote: ").strip()
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"User {email} not found.\n")
                return
            
            if user.is_admin:
                print(f"{email} is already an admin.\n")
                return
            
            user.is_admin = True
            db.session.commit()
            print(f"✓ {email} is now an admin.\n")
        
        elif choice == '2':
            email = input("Enter admin email: ").strip()
            first_name = input("First name: ").strip()
            last_name = input("Last name: ").strip()
            password = input("Password: ").strip()
            
            if len(password) < 6:
                print("Password must be at least 6 characters.\n")
                return
            
            if User.query.filter_by(email=email).first():
                print(f"User {email} already exists.\n")
                return
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_admin=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✓ Admin user {email} created successfully.\n")
        
        else:
            print("Exiting.\n")

if __name__ == '__main__':
    admin_setup()
