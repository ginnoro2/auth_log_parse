import datetime
import random
from faker import Faker
import time
from database import create_connection
import ipaddress

fake = Faker()

class SSHLogSimulator:
    def __init__(self):
        self.connection = create_connection()
        self.cursor = self.connection.cursor()
        self.usernames = ['admin', 'root', 'user', 'jenkins', 'ubuntu', 'system']
        self.passwords = ['password123', 'admin123', 'root123', '123456', 'qwerty']
        
    def generate_random_ip(self):
        """Generate a random IP address"""
        return str(ipaddress.IPv4Address(random.randint(0, 2**32 - 1)))

    def generate_log_entry(self):
        """Generate a single SSH log entry"""
        timestamp = datetime.datetime.now()
        source_ip = self.generate_random_ip()
        username = random.choice(self.usernames)
        password = random.choice(self.passwords)
        # 70% success rate
        status = 'success' if random.random() < 0.7 else 'failed'
        
        # Store password as BLOB (encoded bytes)
        password_blob = password.encode('utf-8')
        attempt_details = f"SSH login attempt from {source_ip}"
        
        query = """
        INSERT INTO auth_logs 
        (timestamp, source_ip, username, encrypted_password, status, attempt_details)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (timestamp, source_ip, username, password_blob, status, attempt_details)
        
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"[{timestamp}] {status.upper()}: Login attempt from {source_ip} for user {username}")
        except Exception as e:
            print(f"Error inserting log entry: {e}")
            self.connection.rollback()

    def run(self, duration_seconds=None, entries_per_second=1):
        """Run the simulator"""
        print("Starting SSH log simulation...")
        start_time = time.time()
        
        try:
            while True:
                self.generate_log_entry()
                time.sleep(1 / entries_per_second)
                
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                    
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up database connections"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("\nSimulation ended. Database connections closed.")

if __name__ == "__main__":
    simulator = SSHLogSimulator()
    # Run simulation for 1 hour (3600 seconds) with 2 entries per second
    simulator.run(duration_seconds=3600, entries_per_second=2) 