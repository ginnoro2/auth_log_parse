#SSH Log Simulator with MySQL Database

This project simulates SSH authentication logs and stores them in a MySQL database. It generates realistic SSH login attempts (both successful and failed) and provides comprehensive testing and monitoring capabilities.

##Quick Start Guide

This walkthrough will help you build, set up, and run the SSH log simulator container, then verify the database setup and check the generated data.

##Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (for macOS/Windows) or **Docker Engine** (for Linux)
- **Docker Compose** (usually included with Docker Desktop)
- **Git** (for cloning the repository)

### Verify Docker Installation

```bash
docker --version
docker-compose --version
```

Expected output:
```
Docker version 20.10.22, build 3a2c30b63a
Docker Compose version v2.32.4-desktop.1
```

##Step 1: Build the Docker Image

First, let's build the Docker image for the SSH log simulator:

```bash
docker-compose build
```

**What this does:**
- Downloads the Python 3.9 slim base image
- Installs MySQL client tools
- Copies and installs Python dependencies from `requirements.txt`
- Copies all application files to the container
- Makes test scripts executable

**Expected output:**
```
[+] Building 103.4s (16/16) FINISHED
 => [internal] booting buildkit
 => pulling image moby/buildkit:buildx-stable-1
 => creating container buildx_buildkit_sweet_joliot0
 => [internal] load build definition from Dockerfile
 => [internal] load metadata for docker.io/library/python:3.9-slim
 => [auth] library/python:pull token for registry-1.docker.io
 => [internal] load .dockerignore
 => [1/8] FROM docker.io/library/python:3.9-slim@sha256:a40cf9eba2c3ed9226afa9ace504f07ad30fe831343bb1c69f7a6707aadb
 => [2/8] RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*
 => [3/8] WORKDIR /app
 => [4/8] COPY requirements.txt .
 => [5/8] RUN pip install --no-cache-dir -r requirements.txt
 => [6/8] COPY . .
 => [7/8] RUN chmod +x test_auth_log.py
 => [8/8] RUN echo '#!/bin/bash\npython test_auth_log.py' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh
 => exporting to docker image format
 => => exporting layers
 => => exporting manifest
 => => exporting config
 => => sending tarball
 => importing to docker
Docker image built successfully
```

## Step 2: Start MySQL Database

Now let's start the MySQL database service:

```bash
docker-compose up -d mysql
```

**What this does:**
- Starts MySQL 8.0 container
- Creates the `ssh_logs` database
- Runs the initialization script (`init.sql`) to create tables
- Sets up health checks

**Expected output:**
```
[+] Running 2/2
 ⠿ Network docker_mysql_default  Created
 ⠿ Container ssh_logs_db         Started
```

## Step 3: Wait for MySQL to be Ready

MySQL needs a few seconds to initialize. Let's wait and check its health:

```bash
sleep 10
docker-compose ps
```

**Expected output:**
```
NAME            COMMAND                  SERVICE             STATUS              PORTS
ssh_logs_db     "docker-entrypoint.s…"   mysql               running (healthy)   0.0.0.0:3306->3306/tcp
```

##Step 4: Verify Database Setup

Let's check if the database and tables were created correctly:

```bash
docker-compose exec mysql mysql -u root -pyour_password -e "SHOW DATABASES;"
```

**Expected output:**
```
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| ssh_logs           |
| sys                |
+--------------------+
```

Now let's check the tables in the `ssh_logs` database:

```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SHOW TABLES;"
```

**Expected output:**
```
+--------------------+
| Tables_in_ssh_logs |
+--------------------+
| auth_logs          |
+--------------------+
```

Let's examine the structure of the `auth_logs` table:

```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; DESCRIBE auth_logs;"
```

# Output
```
+----+---------------------+-----------------+----------+---------+
| id | timestamp           | source_ip       | username | status  |
+----+---------------------+-----------------+----------+---------+
| 42 | 2025-06-18 06:40:40 | 221.120.145.21  | ubuntu   | success |
| 41 | 2025-06-18 06:40:39 | 109.213.109.218 | user     | success |
| 40 | 2025-06-18 06:40:39 | 244.232.206.192 | system   | failed  |
| 38 | 2025-06-18 06:40:38 | 72.185.42.203   | system   | success |
| 39 | 2025-06-18 06:40:38 | 60.135.59.144   | system   | success |
| 36 | 2025-06-18 06:40:37 | 241.146.136.96  | admin    | success |
| 37 | 2025-06-18 06:40:37 | 159.118.161.104 | jenkins  | success |
| 35 | 2025-06-18 06:40:36 | 255.96.112.130  | root     | failed  |
| 34 | 2025-06-18 06:40:36 | 162.106.160.178 | ubuntu   | success |
| 32 | 2025-06-18 06:40:35 | 183.48.40.250   | ubuntu   | success |
+----+---------------------+-----------------+----------+---------+
```

## Step 5: Start the SSH Log Simulator

Now let's start the SSH log simulator to generate authentication logs:

```bash
docker-compose up -d ssh_simulator
```

**What this does:**
- Starts the SSH log simulator container
- Connects to the MySQL database
- Begins generating simulated SSH login attempts
- Stores logs in the `auth_logs` table

**Expected output:**
```
[+] Running 2/2
 ⠿ Container ssh_logs_db    Healthy
 ⠿ Container ssh_simulator  Started
```

## Step 6: Monitor Log Generation

Let's check if logs are being generated in real-time:

```bash
docker-compose logs -f ssh_simulator
```

**Expected output:**
```
ssh_simulator  | [2025-06-12 17:56:31] SUCCESS: Login attempt from 88.147.155.228 for user user
ssh_simulator  | [2025-06-12 17:56:32] FAILED: Login attempt from 242.96.221.204 for user root
ssh_simulator  | [2025-06-12 17:56:33] SUCCESS: Login attempt from 212.31.134.164 for user jenkins
```

**Press Ctrl+C to stop following logs**

## Step 7: Check Database Statistics

Let's see how many log entries have been generated:

```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) as total_entries FROM auth_logs;"
```

**Expected output:**
```
+----------------+
| total_entries  |
+----------------+
| 1886           |
+----------------+
```

Check the distribution of successful vs failed attempts:

```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT status, COUNT(*) as count FROM auth_logs GROUP BY status;"
```

**Expected output:**
```
+---------+-------+
| status  | count |
+---------+-------+
| failed  | 568   |
| success | 1318  |
+---------+-------+
```

## Step 8: View Recent Log Entries

Let's look at the most recent authentication attempts:

```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT id, DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') as timestamp, source_ip, username, status FROM auth_logs ORDER BY timestamp DESC LIMIT 10;"
```

**Expected output:**
```
+------+---------------------+-----------------+----------+---------+
| id   | timestamp           | source_ip       | username | status  |
+------+---------------------+-----------------+----------+---------+
| 1886 | 2025-06-12 17:56:31 | 88.147.155.228  | user     | success |
| 1885 | 2025-06-12 17:56:30 | 242.96.221.204  | root     | failed  |
| 1884 | 2025-06-12 17:56:30 | 212.31.134.164  | jenkins  | success |
| 1883 | 2025-06-12 17:56:29 | 114.237.140.209 | root     | success |
| 1882 | 2025-06-12 17:56:29 | 139.77.0.166    | root     | success |
+------+---------------------+-----------------+----------+---------+
```

## Step 9: Advanced Database Queries

Let's run some more detailed analysis queries:

**Find the most active source IPs:**
```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT source_ip, COUNT(*) as attempts FROM auth_logs GROUP BY source_ip ORDER BY attempts DESC LIMIT 5;"
```

**Find failed login attempts in the last hour:**
```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT timestamp, source_ip, username FROM auth_logs WHERE status='failed' AND timestamp > DATE_SUB(NOW(), INTERVAL 1 HOUR) ORDER BY timestamp DESC;"
```

**Check which usernames are being targeted:**
```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT username, COUNT(*) as attempts FROM auth_logs GROUP BY username ORDER BY attempts DESC;"
```

## Step 10: Run Comprehensive Tests

Let's run the comprehensive test suite to verify everything is working:

```bash
docker-compose run --rm test_service
```

**What this tests:**
- Database connection and table existence
- Auth log insertion and retrieval
- Query functionality
- SSH simulator integration
- Docker environment configuration

## Step 11: Stop the Services

When you're done testing, stop the services:

```bash
docker-compose stop
```

**Expected output:**
```
[+] Running 2/2
 ⠿ Container ssh_simulator  Stopped
 ⠿ Container ssh_logs_db    Stopped
```

## Step 12: Clean Up (Optional)

To completely remove all containers and data:

```bash
docker-compose down -v
```

**What this does:**
- Stops all containers
- Removes containers
- Removes volumes (deletes all database data)
- Removes networks

##Folder Structure

```
docker_mysql/
├── docker-compose.yml      # Docker services configuration
├── Dockerfile             # Python application container
├── init.sql              # Database initialization script
├── requirements.txt       # Python dependencies
├── ssh_log_simulator.py  # Main simulation script
├── database.py           # Database connection utilities
├── test_auth_log.py      # Comprehensive test suite
├── build_and_test.sh     # Automated build and test script
└── keys/                 # Directory for encryption keys
```

## Configuration Options

### Environment Variables

You can customize the setup by modifying environment variables in `docker-compose.yml`:

```yaml
environment:
  MYSQL_HOST: mysql
  MYSQL_USER: root
  MYSQL_PASSWORD: your_password
  MYSQL_DATABASE: ssh_logs
```

### Simulation Parameters

Modify `ssh_log_simulator.py` to change simulation behavior:

- **Duration**: How long to run the simulation
- **Frequency**: How many log entries per second
- **Success rate**: Percentage of successful vs failed attempts
- **Usernames**: List of usernames to simulate
- **Passwords**: List of passwords to simulate

## Troubleshoot if required

### Common Issues

**1. MySQL won't start:**
```bash
docker-compose down -v
docker-compose up -d mysql
```

**2. SSH simulator can't connect to database:**
```bash
docker-compose logs ssh_simulator
# Check if MySQL is healthy
docker-compose ps
```

**3. Permission denied errors:**
```bash
chmod +x build_and_test.sh
chmod +x test_auth_log.py
```

**4. Port conflicts:**
If port 3306 is already in use, modify the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "3307:3306"  # Change 3306 to 3307
```

### Debug Commands

**Check container status:**
```bash
docker-compose ps
```

**View all logs:**
```bash
docker-compose logs
```

**Access MySQL directly:**
```bash
docker-compose exec mysql mysql -u root -pyour_password ssh_logs
```

**Check container resources:**
```bash
docker stats
```

##Monitoring and Analytic

### Real-time Monitoring

** Watch log generation:**
```bash
watch -n 2 'docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) FROM auth_logs;"'
```

** Monitor failed attempts:**
```bash
watch -n 5 'docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) FROM auth_logs WHERE status=\"failed\" AND timestamp > DATE_SUB(NOW(), INTERVAL 5 MINUTE);"'
```

### Performance Queries

**Check database performance:**
```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; EXPLAIN SELECT * FROM auth_logs WHERE status='failed';"
```

**Analyze data distribution:**
```bash
docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT DATE(timestamp) as date, COUNT(*) as entries FROM auth_logs GROUP BY DATE(timestamp) ORDER BY date DESC;"
```

## what Next

1. **Customize the simulation** by modifying `ssh_log_simulator.py`
2. **Add more analysis queries** for security monitoring
3. **Set up automated alerts** for suspicious activity
4. **Implement log retention policies** for production use
5. **Add authentication and authorization** for database access

## Additional Resources 

- [Docker Documentation](https://docs.docker.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Python MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)

---
 
