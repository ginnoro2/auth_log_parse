# Auth.Log Database Testing Guide

This guide explains how to test the auth.log contents stored in the MySQL database using Docker.

## 🚀 Quick Start

### 1. Run the Complete Test Suite
```bash
./build_and_test.sh
```

This script will:
- Build the Docker image
- Start MySQL service
- Run comprehensive database tests
- Test SSH log generation
- Display results and statistics

### 2. Manual Testing Steps

#### Build and Start Services
```bash
# Build the Docker image
docker-compose build

# Start MySQL service
docker-compose up -d mysql

# Wait for MySQL to be ready (about 10-15 seconds)
```

#### Run Database Tests
```bash
# Run comprehensive tests
docker-compose run --rm test_service

# Or run tests with profile
docker-compose --profile test up test_service
```

#### Test SSH Log Generation
```bash
# Start the SSH simulator
docker-compose up -d ssh_simulator

# Check logs in real-time
docker-compose logs -f ssh_simulator

# Stop the simulator
docker-compose stop ssh_simulator
```

## 🧪 Test Components

### 1. Database Connection Test
- Verifies MySQL connection
- Checks database and table existence
- Tests basic query functionality

### 2. Auth Log Insertion Test
- Inserts test authentication entries
- Verifies data integrity
- Tests encryption/decryption of passwords

### 3. Query Tests
- Tests various SQL queries on auth_logs table
- Counts total, successful, and failed attempts
- Retrieves recent entries and top source IPs

### 4. Simulator Integration Test
- Tests SSH log simulator functionality
- Generates sample log entries
- Verifies integration with database

### 5. Docker Environment Test
- Checks environment variables
- Verifies Docker configuration

## 📊 Database Schema

The `auth_logs` table structure:
```sql
CREATE TABLE auth_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    source_ip VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    encrypted_password BLOB,
    status ENUM('success', 'failed') NOT NULL,
    attempt_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Useful Commands

### Check Database Status
```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -pyour_password ssh_logs

# View all auth logs
SELECT * FROM auth_logs ORDER BY timestamp DESC LIMIT 10;

# Count entries by status
SELECT status, COUNT(*) FROM auth_logs GROUP BY status;

# View recent failed attempts
SELECT * FROM auth_logs WHERE status='failed' ORDER BY timestamp DESC LIMIT 5;
```

### Monitor Log Generation
```bash
# Watch SSH simulator logs
docker-compose logs -f ssh_simulator

# Check database in real-time
watch -n 2 'docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) FROM auth_logs;"'
```

### Clean Up
```bash
# Stop all services
docker-compose down

# Remove volumes (clears database)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 🐛 Troubleshooting

### Common Issues

1. **MySQL Connection Failed**
   - Ensure MySQL service is healthy: `docker-compose ps`
   - Check logs: `docker-compose logs mysql`
   - Wait longer for MySQL to initialize

2. **Test Failures**
   - Check if database is initialized: `docker-compose exec mysql mysql -u root -pyour_password -e "SHOW DATABASES;"`
   - Verify table exists: `docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SHOW TABLES;"`

3. **Permission Issues**
   - Make sure build script is executable: `chmod +x build_and_test.sh`
   - Check Docker permissions

### Debug Mode
```bash
# Run with verbose output
docker-compose --verbose up

# Check container status
docker-compose ps

# View all logs
docker-compose logs
```

## 📈 Performance Testing

### Load Testing
```bash
# Run simulator with high frequency
docker-compose run --rm ssh_simulator python -c "
from ssh_log_simulator import SSHLogSimulator
sim = SSHLogSimulator()
sim.run(duration_seconds=60, entries_per_second=10)
"
```

### Database Performance
```bash
# Check query performance
docker-compose exec mysql mysql -u root -pyour_password -e "
USE ssh_logs;
EXPLAIN SELECT * FROM auth_logs WHERE status='failed';
"
```

## ✅ Success Criteria

A successful test run should show:
- ✅ All 5 test categories passed
- ✅ Database connection established
- ✅ Auth log entries inserted and retrieved
- ✅ Encryption/decryption working
- ✅ SSH simulator generating logs
- ✅ Docker environment properly configured

## 📝 Test Results

After running tests, you should see:
- Total auth.log entries count
- Successful vs failed attempts ratio
- Recent log entries with timestamps
- Source IP distribution
- Database performance metrics 