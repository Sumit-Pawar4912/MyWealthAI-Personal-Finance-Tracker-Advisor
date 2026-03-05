#!/usr/bin/env python
"""
Verify that password reset worked - test login with new passwords
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models.models import User
from werkzeug.security import check_password_hash

def verify_passwords():
    """Verify that new passwords work"""
    with app.app_context():
        print("\n" + "="*70)
        print("PASSWORD VERIFICATION TEST")
        print("="*70 + "\n")
        
        test_creds = [
            ('pawar12@gmail.com', 'NewPassword1@pawar12'),
            ('nayan12@gmail.com', 'NewPassword2@nayan12'),
            ('shreyash123@gmail.com', 'NewPassword5@shreyash123'),
        ]
        
        all_passed = True
        for email, password in test_creds:
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"[ERROR] {email}: User not found")
                all_passed = False
                continue
            
            # Test password
            if user.check_password(password):
                admin_status = "[ADMIN]" if user.is_admin else "[USER]"
                print(f"[OK] {email}")
                print(f"   Password: {password[:20]}...")
                print(f"   Status: {admin_status}")
                print(f"   Hash method: {'PBKDF2' if not user.password_hash.startswith('scrypt') else 'SCRYPT'}\n")
            else:
                print(f"[ERROR] {email}: Password verification FAILED")
                all_passed = False
        
        print("="*70)
        if all_passed:
            print("[OK] ALL PASSWORD TESTS PASSED!")
            print("\n[SUCCESS] You can now login to the application!")
            print("\nDefault Admin Account:")
            print(f"  Email: pawar12@gmail.com")
            print(f"  Password: NewPassword1@pawar12")
            print(f"  Access: Admin Panel at /admin")
        else:
            print("[ERROR] SOME PASSWORD TESTS FAILED!")
        print("="*70 + "\n")
        
        return all_passed

if __name__ == '__main__':
    success = verify_passwords()
    sys.exit(0 if success else 1)
