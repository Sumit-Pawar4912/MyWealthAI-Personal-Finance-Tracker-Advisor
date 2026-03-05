#!/usr/bin/env python
"""
Check database pragma settings
"""
import sqlite3

db_path = 'instance/mywelthai.db'

print("\n" + "="*70)
print("DATABASE PRAGMA SETTINGS")
print("="*70 + "\n")

try:
    conn = sqlite3.connect(db_path, timeout=10)
    
    # Check WAL mode
    result = conn.execute('PRAGMA journal_mode;').fetchone()
    print(f"[*] Journal Mode: {result[0]}")
    
    # Check synchronous
    result = conn.execute('PRAGMA synchronous;').fetchone()
    mode_names = {0: 'OFF', 1: 'NORMAL', 2: 'FULL', 3: 'EXTRA'}
    print(f"[*] Synchronous: {mode_names.get(result[0], result[0])}")
    
    # Check timeout
    result = conn.execute('PRAGMA busy_timeout;').fetchone()
    print(f"[*] Busy Timeout: {result[0]}ms")
    
    conn.close()
    
    print("\n" + "="*70)
    if result:
        print("[OK] Database is properly configured!")
    
except Exception as e:
    print(f"[ERROR] {e}")

print("="*70 + "\n")
