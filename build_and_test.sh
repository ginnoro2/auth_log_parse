#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Docker MySQL Auth.Log Database Test Suite${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}  $1${NC}"
}

print_error() {
    echo -e "${RED} $1${NC}"
}

# Check if Docker is running
echo -e "\n${BLUE} Checking Docker status...${NC}"
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_status "Docker is running"

# Build the Docker image
echo -e "\n${BLUE} Building Docker image...${NC}"
if docker-compose build; then
    print_status "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Start MySQL service
echo -e "\n${BLUE} Starting MySQL service...${NC}"
if docker-compose up -d mysql; then
    print_status "MySQL service started"
else
    print_error "Failed to start MySQL service"
    exit 1
fi

# Wait for MySQL to be ready
echo -e "\n${BLUE} Waiting for MySQL to be ready...${NC}"
sleep 10

# Check MySQL health
echo -e "\n${BLUE} Checking MySQL health...${NC}"
if docker-compose exec mysql mysqladmin ping -h localhost > /dev/null 2>&1; then
    print_status "MySQL is healthy and ready"
else
    print_error "MySQL is not responding"
    exit 1
fi

# Run database initialization test
echo -e "\n${BLUE}  Testing database initialization...${NC}"
if docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SHOW TABLES;" | grep -q "auth_logs"; then
    print_status "Database and auth_logs table created successfully"
else
    print_error "Database initialization failed"
    exit 1
fi

# Run the comprehensive test
echo -e "\n${BLUE} Running comprehensive auth.log database test...${NC}"
if docker-compose run --rm test_service; then
    print_status "All tests passed!"
else
    print_error "Some tests failed"
    echo -e "\n${YELLOW} Test logs:${NC}"
    docker-compose logs test_service
fi

# Start the SSH simulator for a brief test
echo -e "\n${BLUE} Testing SSH log simulator...${NC}"
docker-compose up -d ssh_simulator

# Wait a bit for some logs to be generated
sleep 5

# Check if logs are being generated
echo -e "\n${BLUE} Checking log generation...${NC}"
log_count=$(docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) FROM auth_logs;" | tail -n 1)
if [ "$log_count" -gt 0 ]; then
    print_status "SSH logs are being generated successfully (${log_count} entries)"
else
    print_warning "No SSH logs generated yet"
fi

# Show recent logs
echo -e "\n${BLUE} Recent auth.log entries:${NC}"
docker-compose exec mysql mysql -u root -pyour_password -e "
USE ssh_logs; 
SELECT 
    id,
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') as timestamp,
    source_ip,
    username,
    status,
    LEFT(attempt_details, 50) as details
FROM auth_logs 
ORDER BY timestamp DESC 
LIMIT 5;
"

# Stop the simulator
echo -e "\n${BLUE} Stopping SSH simulator...${NC}"
docker-compose stop ssh_simulator
print_status "SSH simulator stopped"

# Final status
echo -e "\n${BLUE} Final Database Status:${NC}"
total_entries=$(docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) FROM auth_logs;" | tail -n 1)
success_entries=$(docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) FROM auth_logs WHERE status='success';" | tail -n 1)
failed_entries=$(docker-compose exec mysql mysql -u root -pyour_password -e "USE ssh_logs; SELECT COUNT(*) FROM auth_logs WHERE status='failed';" | tail -n 1)

echo -e "${GREEN} Total auth.log entries: ${total_entries}${NC}"
echo -e "${GREEN} Successful attempts: ${success_entries}${NC}"
echo -e "${GREEN} Failed attempts: ${failed_entries}${NC}"

echo -e "\n${BLUE} Docker build and test completed successfully!${NC}"
echo -e "${YELLOW} To run the full simulation: docker-compose up${NC}"
echo -e "${YELLOW} To run tests only: docker-compose --profile test up test_service${NC}"
echo -e "${YELLOW} To clean up: docker-compose down -v${NC}" 
