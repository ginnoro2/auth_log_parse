# SSH Log Simulator with RSA Encryption

This project simulates SSH authentication logs with RSA-encrypted storage in MySQL. It generates realistic SSH login attempts (both successful and failed) and stores them securely in a MySQL database using asymmetric encryption.

## Features

- Simulates SSH login attempts with configurable frequency
- Uses RSA asymmetric encryption for password storage
- Stores logs in MySQL with proper indexing
- Provides tools for log analysis and decryption
- Runs entirely in Docker containers

## Prerequisites

- Docker
- Docker Compose
- Git

## Quick Start

1. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd ssh-log-simulator
```

2. Build and start the containers:
```bash
docker-compose up --build -d
```

Expected output:
```
[+] Building ...
[+] Running 4/4
 ⠿ Network docker_mysql_default      Created
 ⠿ Volume "docker_mysql_mysql_data"  Created
 ⠿ Container ssh_logs_db             Healthy
 ⠿ Container ssh_simulator           Started
```

## Verifying the Setup

1. Check if containers are running:
```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                    COMMAND                  STATUS
xxx            mysql:8.0               "docker-entrypoint.s…"   Up (healthy)
xxx            docker_mysql-simulator   "python ssh_log_simu…"   Up
```

2. Check the database structure:
```bash
docker exec -it ssh_logs_db mysql -uroot -pyour_password -e "USE ssh_logs; SHOW TABLES;"
```

Expected output:
```
+--------------------+
| Tables_in_ssh_logs |
+--------------------+
| auth_logs          |
+--------------------+
```

3. View recent log entries:
```bash
docker exec -it ssh_logs_db mysql -uroot -pyour_password -e "USE ssh_logs; SELECT timestamp, source_ip, username, status FROM auth_logs LIMIT 5;"
```

Expected output:
```
+---------------------+-----------------+----------+---------+
| timestamp           | source_ip       | username | status  |
+---------------------+-----------------+----------+---------+
| 2025-06-12 17:38:16 | 106.251.104.146 | admin    | success |
...
```

## Testing Encryption

1. Run the encryption test:
```bash
docker exec -it ssh_simulator python test_encryption.py
```

Expected output:
```
Testing Encryption/Decryption:
Original Password: TestPassword123!
Encrypted Length: 344 bytes
Decrypted Password: TestPassword123!
Encryption Test Passed
```

2. View and decrypt log entries:
```bash
docker exec -it ssh_simulator python decrypt_log.py
```

Expected output:
```
SSH Log Decryption Tool
----------------------
Recent Log Entries:
ID      Timestamp               Source IP               Username        Status
--------------------------------------------------------------------------------
...
Enter the ID of the log entry to decrypt: 
```

## Project Structure

- `docker-compose.yml`: Docker services configuration
- `Dockerfile`: Python application container configuration
- `init.sql`: Database initialization script
- `ssh_log_simulator.py`: Main simulation script
- `encryption.py`: RSA encryption/decryption utilities
- `decrypt_log.py`: Tool for viewing and decrypting logs
- `test_encryption.py`: Encryption testing utility

## Security Notes

- RSA key pair is automatically generated on first run
- Private key is stored in the mounted `keys` directory
- Passwords are encrypted with 2048-bit RSA
- Database credentials should be changed in production

## Stopping the System

To stop the containers:
```bash
docker-compose down
```

To stop and remove all data (including volumes):
```bash
docker-compose down -v
```

## Monitoring Logs

View SSH simulator logs:
```bash
docker logs -f ssh_simulator
```

View MySQL logs:
```bash
docker logs -f ssh_logs_db
```

## Troubleshooting

1. If MySQL fails to start:
```bash
docker-compose down -v
docker-compose up --build -d
```

2. If encryption keys are not generated:
```bash
docker exec -it ssh_simulator rm -rf /app/keys/*
docker-compose restart ssh_simulator
```

3. To reset the database:
```bash
docker-compose down -v
docker-compose up --build -d
```

## Production Considerations

1. Change default passwords in `docker-compose.yml`
2. Secure the `keys` directory with appropriate permissions
3. Configure proper logging and monitoring
4. Set up regular database backups
5. Use Docker secrets for sensitive information

## Contributing

Feel free to submit issues and enhancement requests! 