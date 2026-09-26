CREATE DATABASE IF NOT EXISTS emergency_db;
USE emergency_db;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('citizen','operator','admin') DEFAULT 'citizen'
);

CREATE TABLE IF NOT EXISTS resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('ambulance','fire_truck') NOT NULL,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    status ENUM('available','dispatched') DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS emergencies (
    emergency_id INT AUTO_INCREMENT PRIMARY KEY,
    reported_by INT NOT NULL,
    type ENUM('fire','medical','accident') NOT NULL,
    severity ENUM('low','medium','high','critical') NOT NULL,
    people_affected INT NOT NULL DEFAULT 1,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    priority_score FLOAT NOT NULL,
    status ENUM('reported','assigned','resolved') DEFAULT 'reported',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reported_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS dispatches (
    dispatch_id INT AUTO_INCREMENT PRIMARY KEY,
    emergency_id INT NOT NULL,
    resource_id INT NOT NULL,
    distance_km DECIMAL(10,2),
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emergency_id) REFERENCES emergencies(emergency_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    UNIQUE KEY one_dispatch_per_emergency (emergency_id)
);

CREATE OR REPLACE VIEW active_emergencies AS
SELECT e.*, u.name AS reported_by_name
FROM emergencies e
JOIN users u ON e.reported_by = u.user_id
WHERE e.status <> 'resolved'
ORDER BY e.priority_score DESC, e.created_at ASC;

DROP TRIGGER IF EXISTS after_dispatch_insert;
DELIMITER //
CREATE TRIGGER after_dispatch_insert
AFTER INSERT ON dispatches
FOR EACH ROW
BEGIN
    UPDATE resources SET status = 'dispatched' WHERE resource_id = NEW.resource_id;
    UPDATE emergencies SET status = 'assigned' WHERE emergency_id = NEW.emergency_id;
END//
DELIMITER ;
