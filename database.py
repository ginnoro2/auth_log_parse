import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'your_password'),
            database=os.getenv('MYSQL_DATABASE', 'ssh_logs')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def create_database():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'your_password')
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS ssh_logs")
        
        # Use the database
        cursor.execute("USE ssh_logs")
        
        # Create auth_logs table with encryption support
        create_table_query = """
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            source_ip VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            encrypted_password BLOB,
            status ENUM('success', 'failed') NOT NULL,
            attempt_details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        
        # Create indexes
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON auth_logs(timestamp)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_status ON auth_logs(status)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_source_ip ON auth_logs(source_ip)
        """)
        
        connection.commit()
        print("Database and tables created successfully!")
        
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database() 