#!/usr/bin/env python
"""
Password Reset Script - Create admin and reset corrupted scrypt passwords
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models.models import User
from werkzeug.security import generate_password_hash

def reset_passwords():
    """Reset all corrupted scrypt passwords to PBKDF2-hashed passwords"""
    with app.app_context():
        print("\n" + "="*70)
        print("PASSWORD RESET SCRIPT")
        print("="*70)
        
        # Get all users
        users = User.query.all()
        if not users:
            print("ERROR: No users found in database")
            return False
        
        print(f"\nFound {len(users)} users in database:\n")
        for user in users:
            print(f"  * {user.email}")
        
        # Create/promote first user to admin
        first_user = users[0]
        first_user.is_admin = True
        
        # Update all users with new passwords
        print(f"\n[*] Resetting passwords...\n")
        password_map = {}
        
        for i, user in enumerate(users, 1):
            # Generate new password for each user
            new_pwd = f"NewPassword{i}@{user.email.split('@')[0]}"
            # Force PBKDF2 method instead of scrypt
            user.password_hash = generate_password_hash(new_pwd, method='pbkdf2:sha256')
            password_map[user.email] = {
                'password': new_pwd,
                'is_admin': i == 1  # First user is admin
            }
            print(f"  [{i}/{len(users)}] {user.email}")
            print(f"      Password: {new_pwd}")
            print(f"      Admin: {i == 1}\n")
        
        # Commit all changes
        try:
            db.session.commit()
            print("="*70)
            print("[OK] PASSWORD RESET SUCCESSFUL!")
            print("="*70)
            print("\n[INFO] NEW CREDENTIALS:\n")
            for email, creds in password_map.items():
                print(f"  Email: {email}")
                print(f"  Password: {creds['password']}")
                print(f"  Admin: {'Yes' if creds['is_admin'] else 'No'}\n")
            
            print("="*70)
            print("[INFO] NEXT STEPS:")
            print("  1. Start the backend: python run.py")
            print("  2. Visit: http://localhost:5173/login")
            print(f"  3. Login with: {users[0].email} / {password_map[users[0].email]['password']}")
            print("  4. Admin panel accessible at: /admin")
            print("="*70 + "\n")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error saving passwords: {e}")
            return False

if __name__ == '__main__':
    success = reset_passwords()
    sys.exit(0 if success else 1)
