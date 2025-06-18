from encryption import encrypt_data, decrypt_data
import mysql.connector
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'your_password'),
        database=os.getenv('MYSQL_DATABASE', 'ssh_logs')
    )

def test_encryption():
    # Test data
    test_password = "TestPassword123!"
    
    print("\nTesting Encryption/Decryption:")
    print(f"Original Password: {test_password}")
    
    # Encrypt the password
    encrypted = encrypt_data(test_password)
    print(f"Encrypted Length: {len(encrypted)} bytes")
    
    # Decrypt the password
    decrypted = decrypt_data(encrypted)
    print(f"Decrypted Password: {decrypted}")
    
    # Verify
    print(f"Encryption Test {'Passed' if test_password == decrypted else 'Failed'}")
    
    # Store test entry in database
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO auth_logs 
            (timestamp, source_ip, username, encrypted_password, status, attempt_details)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datetime.datetime.now(),
            '127.0.0.1',
            'test_user',
            encrypted,
            'success',
            'Test encryption entry'
        ))
        
        test_id = cursor.lastrowid
        conn.commit()
        print(f"\nTest entry stored in database with ID: {test_id}")
        
    except Exception as e:
        print(f"Error storing test entry: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_encryption() 