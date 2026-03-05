#!/usr/bin/env python
"""
Check database password hashes to see if reset worked
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models.models import User

def check_hashes():
    """Check what's stored in database"""
    with app.app_context():
        print("\n" + "="*70)
        print("DATABASE PASSWORD HASH CHECK")
        print("="*70 + "\n")
        
        users = User.query.all()
        for user in users:
            hash_prefix = user.password_hash[:20]
            if user.password_hash.startswith('scrypt'):
                hash_type = "SCRYPT (legacy - corrupted)"
                color = "[FAIL]"
            elif user.password_hash.startswith('pbkdf2'):
                hash_type = "PBKDF2 (new - working)"
                color = "[OK]"
            else:
                hash_type = "UNKNOWN"
                color = "[?]"
            
            admin_str = " (ADMIN)" if user.is_admin else ""
            print(f"{color} {user.email}{admin_str}")
            print(f"   Type: {hash_type}")
            print(f"   Hash: {hash_prefix}...{user.password_hash[-10:]}")
            print()
        
        print("="*70)

if __name__ == '__main__':
    check_hashes()
