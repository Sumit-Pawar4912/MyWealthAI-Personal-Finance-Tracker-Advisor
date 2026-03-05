#!/usr/bin/env python
"""
Enable WAL mode on SQLite database for concurrent access
"""
import sqlite3
import time
import sys

try:
    # Try to connect with long timeout
    print("[*] Connecting to database...", flush=True)
    sys.stdout.flush()
    
    # Use 30 second timeout and autocommit mode
    conn = sqlite3.connect('instance/mywelthai.db', timeout=30)
    conn.isolation_level = None  # Autocommit mode
    
    # Get cursor
    cursor = conn.cursor()
    
    print("[*] Setting journal_mode=WAL...", flush=True)
    sys.stdout.flush()
    cursor.execute('PRAGMA journal_mode=WAL')
    result = cursor.fetchone()
    print(f"[OK] Journal mode: {result[0] if result else 'WAL'}", flush=True)
    sys.stdout.flush()
    
    print("[*] Setting synchronous=NORMAL...", flush=True)
    sys.stdout.flush()
    cursor.execute('PRAGMA synchronous=NORMAL')
    print(f"[OK] Synchronous mode set", flush=True)
    sys.stdout.flush()
    
    print("[*] Setting busy_timeout=10000...", flush=True)
    sys.stdout.flush()
    cursor.execute('PRAGMA busy_timeout=10000')
    print(f"[OK] Timeout set to 10 seconds", flush=True)
    sys.stdout.flush()
    
    cursor.close()
    conn.close()
    
    print("\n[OK] Database optimized for concurrent access!", flush=True)
    sys.stdout.flush()
    
except Exception as e:
    print(f"[ERROR] {e}", flush=True)
    sys.stdout.flush()
    sys.exit(1)

