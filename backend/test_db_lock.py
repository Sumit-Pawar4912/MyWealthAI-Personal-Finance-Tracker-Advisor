#!/usr/bin/env python
"""
Test script to trigger database locked error
"""
import requests
import json
import concurrent.futures
import time

BASE_URL = "http://localhost:5000"

def register_user(email, password):
    """Try to register a user"""
    print(f"[*] Registering {email}...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": email, "password": password},
            timeout=20
        )
        print(f"[{response.status_code}] {email}")
        if response.status_code != 201:
            print(f"     ERROR: {response.text[:200]}")
        return response.status_code, response.text
    except Exception as e:
        print(f"[ERROR] {email}: {str(e)[:100]}")
        return None, str(e)

def test_concurrent_registrations():
    """Test concurrent user registrations to trigger lock"""
    print("\n" + "="*70)
    print("TESTING CONCURRENT REGISTRATIONS")
    print("="*70 + "\n")
    
    # Prepare test data
    test_users = []
    for i in range(1, 6):
        test_users.append((f"testuser{i}@example.com", f"Password{i}@123"))
    
    print(f"[*] Attempting to register {len(test_users)} users concurrently...\n")
    
    # Make concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(register_user, email, pwd)
            for email, pwd in test_users
        ]
        
        results = list(concurrent.futures.as_completed(futures))
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70 + "\n")
    
    for i, future in enumerate(results):
        try:
            status, text = future.result()
            if status:
                print(f"[{status}] Request {i+1}")
            else:
                print(f"[TIMEOUT] Request {i+1}")
        except Exception as e:
            print(f"[EXCEPTION] Request {i+1}: {str(e)[:100]}")

def test_login_during_register():
    """Test login while registration is happening"""
    print("\n" + "="*70)
    print("TESTING LOGIN DURING REGISTRATION")
    print("="*70 + "\n")
    
    def login():
        print("[*] Attempting login...")
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "pawar12@gmail.com", "password": "NewPassword1@pawar12"},
                timeout=20
            )
            print(f"[{response.status_code}] Login attempt")
            if "database is locked" in response.text.lower():
                print("[!!!] DATABASE LOCKED ERROR DETECTED!")
                print(response.text)
                return True
            return False
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            if "database is locked" in str(e).lower():
                print("[!!!] DATABASE LOCKED ERROR DETECTED!")
                return True
            return False
    
    def register():
        print("[*] Attempting registration...")
        try:
            for i in range(3):
                response = requests.post(
                    f"{BASE_URL}/api/auth/register",
                    json={"email": f"testuser{i}@example.com", "password": "Test@123"},
                    timeout=20
                )
                print(f"[{response.status_code}] Registration attempt {i+1}")
                if "database is locked" in response.text.lower():
                    print("[!!!] DATABASE LOCKED ERROR DETECTED!")
                    print(response.text)
                    return True
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            if "database is locked" in str(e).lower():
                print("[!!!] DATABASE LOCKED ERROR DETECTED!")
                return True
        return False
    
    # Run both concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(login)
        f2 = executor.submit(register)
        
        concurrent.futures.wait([f1, f2])
        
    print("\n" + "="*70)

if __name__ == "__main__":
    print("[Waiting 2 seconds for server to start...]")
    time.sleep(2)
    
    try:
        # Check if server is running
        print("[*] Checking if server is running...")
        requests.get(f"{BASE_URL}/health", timeout=5)
        print("[OK] Server is running\n")
    except Exception as e:
        print(f"[ERROR] Server not running: {e}")
        print("Please start the backend: python run.py")
        exit(1)
    
    # Run tests
    test_concurrent_registrations()
    time.sleep(1)
    test_login_during_register()
