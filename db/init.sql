CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    product VARCHAR(255) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    order_date DATETIME NOT NULL,
    INDEX idx_order_date (order_date),
    INDEX idx_category (category),
    INDEX idx_country (country)
);
