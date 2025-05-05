DROP DATABASE IF EXISTS pharma_bot;
CREATE DATABASE pharma_bot;
USE pharma_bot;

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE users ADD role ENUM('user', 'admin') DEFAULT 'user';

-- ORDERS TABLE with custom order_id (VARCHAR) instead of AUTO_INCREMENT
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(20) UNIQUE,
    user_email VARCHAR(100),
    medicine_name VARCHAR(100),
    quantity INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email)
);

-- FEEDBACK TABLE
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100),
    rating VARCHAR(10),
    comment TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email)
);

-- MEDICINES TABLE
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2),
    stock_quantity INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DUMMY USERS
INSERT INTO users (full_name, email, password) VALUES
('Ayesha Khan', 'ayesha@example.com', 'hashed_password_1'),
('Ali Raza', 'ali@example.com', 'hashed_password_2'),
('Sara Malik', 'sara@example.com', 'hashed_password_3');

-- DUMMY ORDERS with custom order_id
INSERT INTO orders (order_id, user_email, medicine_name, quantity) VALUES
('ORD100001', 'ayesha@example.com', 'Panadol', 2),
('ORD100002', 'ali@example.com', 'Ventolin', 1),
('ORD100003', 'sara@example.com', 'Aspirin', 3),
('ORD100004', 'ayesha@example.com', 'Augmentin', 1);

-- DUMMY FEEDBACK
INSERT INTO feedback (user_email, rating, comment) VALUES
('ayesha@example.com', '5', 'Very fast delivery and helpful chatbot.'),
('ali@example.com', '4', 'Good service but medicine list can be improved.'),
('sara@example.com', '5', 'Excellent support and intuitive UI.');
