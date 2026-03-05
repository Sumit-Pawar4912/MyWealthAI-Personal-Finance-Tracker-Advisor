#!/usr/bin/env python
"""
Simple database check without importing app
"""
import sqlite3
import os

db_path = 'instance/mywelthai.db'

if not os.path.exists(db_path):
    print(f"[ERROR] Database not found at {db_path}")
    exit(1)

print("\n" + "="*70)
print("DATABASE CONTENTS CHECK")
print("="*70 + "\n")

try:
    conn = sqlite3.connect(db_path, timeout=5)
    cursor = conn.cursor()
    
    # Check users table
    print("[*] Checking users table...\n")
    cursor.execute("""
        SELECT email, password_hash, is_admin 
        FROM users 
        ORDER BY email
    """)
    
    users = cursor.fetchall()
    if users:
        print(f"[INFO] Found {len(users)} users:\n")
        for email, hash_val, is_admin in users:
            if hash_val.startswith('pbkdf2'):
                hash_type = "[OK] PBKDF2"
            elif hash_val.startswith('scrypt'):
                hash_type = "[FAIL] SCRYPT"
            else:
                hash_type = "[?] UNKNOWN"
            
            admin_str = " (ADMIN)" if is_admin else ""
            print(f"{hash_type} {email}{admin_str}")
            print(f"        Hash: {hash_val[:30]}...\n")
    else:
        print("[INFO] No users found in database!\n")
    
    conn.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("="*70)
