#!/usr/bin/env python
"""
Configure SQLite database for WAL mode and concurrent access
"""
import sqlite3
import os

db_path = 'instance/mywelthai.db'

if not os.path.exists(db_path):
    print(f"[ERROR] Database not found: {db_path}")
    exit(1)

try:
    # Connect with longer timeout
    conn = sqlite3.connect(db_path, timeout=30)
    
    print("[*] Configuring SQLite for concurrent access...")
    
    # Enable WAL mode
    conn.execute('PRAGMA journal_mode=WAL')
    result = conn.execute('PRAGMA journal_mode').fetchone()[0]
    print(f"[1] Journal mode: {result}")
    
    # Set longer timeout
    conn.execute('PRAGMA busy_timeout=25000')
    print(f"[2] Busy timeout: 25000ms")
    
    # Reduce synchronous for faster writes (WAL provides safety)
    conn.execute('PRAGMA synchronous=NORMAL')
    print(f"[3] Synchronous mode: NORMAL")
    
    # Increase cache for better performance
    conn.execute('PRAGMA cache_size=10000')
    print(f"[4] Cache size: 10000")
    
    # Allow temp stores in memory
    conn.execute('PRAGMA temp_store=MEMORY')
    print(f"[5] Temp store: MEMORY")
    
    conn.commit()
    conn.close()
    
    print("\n[OK] Database configured for concurrent access!")
    print("     Use WAL mode for concurrent reads while writes happen")
    
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)
