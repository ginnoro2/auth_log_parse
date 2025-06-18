#!/usr/bin/env python3
"""
Simple test script to verify auth.log database functionality
"""

import sys
import os
from datetime import datetime
from database import create_connection
from ssh_log_simulator import SSHLogSimulator

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        connection = create_connection()
        if connection is None:
            print("Failed to connect to database")
            return False
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"Connected to MySQL version: {version[0]}")
        
        cursor.execute("SHOW TABLES LIKE 'auth_logs'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("auth_logs table exists")
        else:
            print("auth_logs table does not exist")
            return False
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def test_auth_log_insertion():
    """Test inserting auth log entries"""
    print("\nTesting auth log insertion...")
    
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Insert test entry
        test_timestamp = datetime.now()
        test_source_ip = "192.168.1.100"
        test_username = "test_user"
        test_password = "test_password123"
        test_status = "failed"
        test_details = "Test authentication attempt"
        
        insert_query = """
        INSERT INTO auth_logs 
        (timestamp, source_ip, username, encrypted_password, status, attempt_details)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            test_timestamp, test_source_ip, test_username, 
            test_password.encode(), test_status, test_details
        ))
        connection.commit()
        
        # Verify insertion
        cursor.execute("SELECT * FROM auth_logs WHERE username = %s", (test_username,))
        result = cursor.fetchone()
        
        if result:
            print("Test auth log entry inserted successfully")
            print(f"   - ID: {result[0]}")
            print(f"   - Timestamp: {result[1]}")
            print(f"   - Source IP: {result[2]}")
            print(f"   - Username: {result[3]}")
            print(f"   - Status: {result[5]}")
            print("Password stored as BLOB")
        else:
            print("Test auth log entry not found")
            return False
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Auth log insertion test failed: {e}")
        return False

def test_auth_log_queries():
    """Test various queries on auth_logs table"""
    print("\nTesting auth log queries...")
    
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Test count query
        cursor.execute("SELECT COUNT(*) FROM auth_logs")
        total_count = cursor.fetchone()[0]
        print(f"Total auth log entries: {total_count}")
        
        # Test recent entries
        cursor.execute("""
            SELECT timestamp, source_ip, username, status 
            FROM auth_logs 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        recent_entries = cursor.fetchall()
        print(f"Recent entries retrieved: {len(recent_entries)}")
        
        # Test failed attempts
        cursor.execute("SELECT COUNT(*) FROM auth_logs WHERE status = 'failed'")
        failed_count = cursor.fetchone()[0]
        print(f"Failed attempts: {failed_count}")
        
        # Test successful attempts
        cursor.execute("SELECT COUNT(*) FROM auth_logs WHERE status = 'success'")
        success_count = cursor.fetchone()[0]
        print(f"Successful attempts: {success_count}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Auth log queries test failed: {e}")
        return False

def test_simulator_integration():
    """Test the SSH log simulator integration"""
    print("\nTesting SSH log simulator integration...")
    
    try:
        # Run simulator for a short duration
        simulator = SSHLogSimulator()
        
        # Generate a few test entries
        for i in range(3):
            simulator.generate_log_entry()
        
        simulator.cleanup()
        print("SSH log simulator integration test completed")
        return True
        
    except Exception as e:
        print(f"SSH log simulator integration test failed: {e}")
        return False

def run_simple_test():
    """Run all tests"""
    print("Starting simple auth.log database test...")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Auth Log Insertion", test_auth_log_insertion),
        ("Auth Log Queries", test_auth_log_queries),
        ("Simulator Integration", test_simulator_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"{test_name}: PASSED")
            else:
                print(f"{test_name}: FAILED")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Auth.log database functionality is working correctly.")
        return True
    else:
        print("Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_simple_test()
    sys.exit(0 if success else 1) 
