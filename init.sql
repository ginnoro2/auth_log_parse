CREATE DATABASE IF NOT EXISTS ssh_logs;
USE ssh_logs;

DROP TABLE IF EXISTS auth_logs;
CREATE TABLE auth_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    source_ip VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    encrypted_password BLOB,
    status ENUM('success', 'failed') NOT NULL,
    attempt_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (status),
    INDEX idx_source_ip (source_ip)
); 