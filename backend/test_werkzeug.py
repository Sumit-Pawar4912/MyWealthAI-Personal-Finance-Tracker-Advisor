#!/usr/bin/env python
"""
Test what hash werkzeug.security generates
"""
from werkzeug.security import generate_password_hash, check_password_hash

password = "TestPassword123"
hash1 = generate_password_hash(password)
print(f"Generated hash:\n{hash1}\n")

# Try to verify it
check1 = check_password_hash(hash1, password)
print(f"Verification result: {check1}\n")

# Generate another to compare
hash2 = generate_password_hash(password)
print(f"Second hash:\n{hash2}\n")

# Check if they're different (they should be due to salt)
print(f"Hashes different (expected): {hash1 != hash2}\n")

# Check hash type
if hash1.startswith('scrypt'):
    print("⚠️  Werkzeug is generating SCRYPT hashes!")
elif hash1.startswith('pbkdf2'):
    print("✅ Werkzeug is generating PBKDF2 hashes")
else:
    print(f"❓ Unknown hash type: {hash1[:30]}")
