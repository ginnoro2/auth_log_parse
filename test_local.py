#!/usr/bin/env python3
"""
Local test script to verify auth.log database functionality
This can be run without Docker for development and testing.
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from database import create_connection, create_database
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        return False
    
    try:
        from encryption import encrypt_data, decrypt_data
        print("✅ Encryption module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import encryption module: {e}")
        return False
    
    try:
        from ssh_log_simulator import SSHLogSimulator
        print("✅ SSH log simulator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SSH log simulator: {e}")
        return False
    
    return True

def test_encryption():
    """Test encryption/decryption functionality"""
    print("\n🔍 Testing encryption functionality...")
    
    try:
        from encryption import encrypt_data, decrypt_data
        
        test_password = "test_password_123"
        encrypted = encrypt_data(test_password)
        decrypted = decrypt_data(encrypted)
        
        if decrypted == test_password:
            print("✅ Encryption/decryption working correctly")
            return True
        else:
            print("❌ Encryption/decryption failed")
            return False
            
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

def test_database_schema():
    """Test database schema creation"""
    print("\n🔍 Testing database schema...")
    
    try:
        from database import create_database
        
        # This will create the database and tables if they don't exist
        create_database()
        print("✅ Database schema creation completed")
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False

def test_connection_without_db():
    """Test database connection without requiring MySQL to be running"""
    print("\n🔍 Testing database connection logic...")
    
    try:
        from database import create_connection
        
        # Test with invalid host (should fail gracefully)
        original_host = os.getenv('MYSQL_HOST')
        os.environ['MYSQL_HOST'] = 'invalid_host'
        
        connection = create_connection()
        if connection is None:
            print("✅ Database connection handles errors gracefully")
        else:
            print("⚠️  Database connection succeeded with invalid host")
        
        # Restore original environment
        if original_host:
            os.environ['MYSQL_HOST'] = original_host
        else:
            os.environ.pop('MYSQL_HOST', None)
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_ssh_simulator_logic():
    """Test SSH simulator logic without database connection"""
    print("\n🔍 Testing SSH simulator logic...")
    
    try:
        from ssh_log_simulator import SSHLogSimulator
        import random
        
        # Test IP generation
        simulator = SSHLogSimulator()
        test_ip = simulator.generate_random_ip()
        
        if test_ip and '.' in test_ip:
            print(f"✅ IP generation working: {test_ip}")
        else:
            print("❌ IP generation failed")
            return False
        
        # Test log entry generation logic
        timestamp = datetime.now()
        source_ip = simulator.generate_random_ip()
        username = random.choice(simulator.usernames)
        password = random.choice(simulator.passwords)
        status = 'success' if random.random() < 0.7 else 'failed'
        
        print(f"✅ Log entry generation working:")
        print(f"   - Timestamp: {timestamp}")
        print(f"   - Source IP: {source_ip}")
        print(f"   - Username: {username}")
        print(f"   - Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ SSH simulator logic test failed: {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration files"""
    print("\n🔍 Testing Docker configuration...")
    
    required_files = [
        'Dockerfile',
        'docker-compose.yml',
        'requirements.txt',
        'init.sql'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing files: {missing_files}")
        return False
    
    # Test Dockerfile syntax
    try:
        with open('Dockerfile', 'r') as f:
            dockerfile_content = f.read()
        
        if 'FROM python:' in dockerfile_content and 'WORKDIR /app' in dockerfile_content:
            print("✅ Dockerfile syntax looks correct")
        else:
            print("❌ Dockerfile syntax issues detected")
            return False
            
    except Exception as e:
        print(f"❌ Error reading Dockerfile: {e}")
        return False
    
    return True

def test_requirements():
    """Test requirements.txt"""
    print("\n🔍 Testing requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        required_packages = [
            'mysql-connector-python',
            'cryptography',
            'python-dotenv',
            'faker'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            if any(package in req for req in requirements):
                print(f"✅ {package} found in requirements")
            else:
                print(f"❌ {package} missing from requirements")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️  Missing packages: {missing_packages}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def run_local_tests():
    """Run all local tests"""
    print("🚀 Starting local auth.log database tests...")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Encryption", test_encryption),
        ("Database Schema", test_database_schema),
        ("Database Connection Logic", test_connection_without_db),
        ("SSH Simulator Logic", test_ssh_simulator_logic),
        ("Docker Configuration", test_docker_configuration),
        ("Requirements", test_requirements)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All local tests passed!")
        print("\n💡 Next steps:")
        print("   1. Start Docker Desktop")
        print("   2. Run: ./build_and_test.sh")
        print("   3. Or run: docker-compose up")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_local_tests()
    sys.exit(0 if success else 1) 