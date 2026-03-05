"""
Diagnostic script to inspect stored password hash and test verification
"""

from app import app, db
from app.models import User
import binascii
import base64

def diagnose_password():
    """Check stored password hash and test verification"""
    with app.app_context():
        user = User.query.filter_by(email='pawar12@gmail.com').first()
        
        if not user:
            print("❌ User pawar12@gmail.com not found")
            return
        
        print("📋 USER PASSWORD DIAGNOSIS")
        print("=" * 70)
        print(f"Email: {user.email}")
        print(f"Stored hash: {user.password_hash}")
        print()
        
        # Parse the hash
        if user.password_hash.startswith('scrypt:'):
            print("✅ Hash format: SCRYPT (legacy)")
            parts = user.password_hash.split('$')
            print(f"Parts count: {len(parts)}")
            for i, part in enumerate(parts):
                preview = part[:50] + ('...' if len(part) > 50 else '')
                print(f"Part {i}: {preview}")
            
            if len(parts) >= 3:
                # Parts[0] = scrypt:32768:8:1
                # Parts[1] = salt
                # Parts[2] = hash
                print()
                print("🔍 SALT ANALYSIS:")
                salt_str = parts[1]
                print(f"  Salt string: {salt_str}")
                print(f"  Salt length: {len(salt_str)}")
                
                try:
                    salt_bytes = bytes.fromhex(salt_str)
                    print(f"  ✅ Hex decode succeeded: {len(salt_bytes)} bytes")
                except ValueError as e:
                    print(f"  ❌ Hex decode failed: {e}")
                
                print()
                print("🔍 HASH ANALYSIS:")
                hash_str = parts[2]
                print(f"  Hash string: {hash_str[:50]}...")
                print(f"  Hash length: {len(hash_str)}")
                
                try:
                    hash_bytes = bytes.fromhex(hash_str)
                    print(f"  ✅ Hex decode succeeded: {len(hash_bytes)} bytes")
                except ValueError as e:
                    print(f"  ❌ Hex decode failed: {e}")
        
        elif user.password_hash.startswith('pbkdf2:'):
            print("✅ Hash format: PBKDF2 (new)")
        
        else:
            print(f"❓ Unknown hash format: {user.password_hash[:50]}")
        
        print()
        print("=" * 70)
        
        # Test with known password
        print()
        print("🧪 PASSWORD VERIFICATION TEST:")
        test_passwords = [
            'pawar123',
            'password123',
            'Pawar@123',
            'Pawar123',
        ]
        
        for pwd in test_passwords:
            result = user.check_password(pwd)
            status = "✅" if result else "❌"
            print(f"{status} Password '{pwd}': {result}")
        
        print()
        print("💡 RECOMMENDATION:")
        print("If none of the passwords above work, the stored hash is corrupted.")
        print("Solution: Reset the password using admin_setup.py option 1")
        print("  $ python admin_setup.py")
        print("  Select: 1 (Promote existing user to admin)")
        print("  Or create new admin account with option 2")

if __name__ == '__main__':
    diagnose_password()
