-- ============================================
-- Northwind Schema Exploration
-- Sprint Day 3 | May 25, 2026
-- Goal: Understand dataset structure before analysis
-- Tables: customers, orders, order_details, products,
--         categories, employees, shippers, suppliers,
--         customer_group_thresholds
-- ============================================

SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'northwind';

SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'northwind'
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SHOW TABLES;

DESCRIBE categories;
DESCRIBE customers;
DESCRIBE employees;
DESCRIBE orders;
DESCRIBE order_details;
DESCRIBE products;
DESCRIBE shippers;
DESCRIBE suppliers;

-- --------------------------------------------------------
-- 1. Row counts across all tables
SELECT 'customers' AS tbl, COUNT(*) AS `rows` FROM customers
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_details', COUNT(*) FROM order_details
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'employees', COUNT(*) FROM employees
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'shippers', COUNT(*) FROM shippers
UNION ALL SELECT 'customer_group_thresholds', COUNT(*) FROM customer_group_thresholds;

-- 2. What product categories exist?
SELECT category_id, category_name, `description` FROM categories;

-- 3. Sample of products — price range, stock levels
SELECT product_id, product_name, category_id, supplier_id, 
       unit_price, unit_in_stock, discontinued
FROM products
LIMIT 20;

-- 4. One complete order traced end-to-end
SELECT 
  o.order_id, o.customer_id, o.employee_id, o.order_date, o.shipped_date,
  od.product_id, od.quantity, od.unit_price, od.discount
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
WHERE o.order_id = 10248;

-- 5. Customer distribution by country
SELECT country, COUNT(*) AS customer_count
FROM customers
GROUP BY country
ORDER BY customer_count DESC;

-- 6. What time period does the data cover?
SELECT MIN(order_date) AS first_order, MAX(order_date) AS last_order 
FROM orders;

-- 7. What does customer_group_thresholds look like — and can any customer be mapped to a tier?
SELECT * FROM customer_group_thresholds;

-- After seeing the above, try mapping customers by their total spend:
SELECT 
  c.customer_id,
  c.company_name,
  SUM(od.quantity * od.unit_price) AS total_spend
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.customer_id, c.company_name
ORDER BY total_spend DESC
LIMIT 10;

-- 8. Discontinued products that still appear in past orders
SELECT p.product_name, p.discontinued, COUNT(od.order_id) AS times_ordered
FROM products p
LEFT JOIN order_details od ON p.product_id = od.product_id
WHERE p.discontinued = 1
GROUP BY p.product_id, p.product_name, p.discontinued;













