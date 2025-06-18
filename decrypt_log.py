import mysql.connector
from encryption import decrypt_data
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'your_password'),
        database=os.getenv('MYSQL_DATABASE', 'ssh_logs')
    )

def decrypt_log_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, timestamp, source_ip, username, encrypted_password, status, attempt_details
            FROM auth_logs
            WHERE id = %s
        """, (entry_id,))
        
        entry = cursor.fetchone()
        if entry:
            decrypted_password = decrypt_data(entry['encrypted_password'])
            print("\nDecrypted Log Entry:")
            print(f"ID: {entry['id']}")
            print(f"Timestamp: {entry['timestamp']}")
            print(f"Source IP: {entry['source_ip']}")
            print(f"Username: {entry['username']}")
            print(f"Original Password: {decrypted_password}")
            print(f"Status: {entry['status']}")
            print(f"Details: {entry['attempt_details']}")
        else:
            print(f"No entry found with ID {entry_id}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def show_recent_entries(limit=5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, timestamp, source_ip, username, status
            FROM auth_logs
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        
        print("\nRecent Log Entries:")
        print("ID\tTimestamp\t\tSource IP\t\tUsername\tStatus")
        print("-" * 80)
        
        for entry in cursor.fetchall():
            print(f"{entry['id']}\t{entry['timestamp']}\t{entry['source_ip']}\t{entry['username']}\t{entry['status']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("SSH Log Decryption Tool")
    print("----------------------")
    
    # Show recent entries
    show_recent_entries()
    
    # Ask for an entry to decrypt
    try:
        entry_id = int(input("\nEnter the ID of the log entry to decrypt: "))
        decrypt_log_entry(entry_id)
    except ValueError:
        print("Please enter a valid numeric ID") 