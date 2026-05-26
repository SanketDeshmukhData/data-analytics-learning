-- ============================================
-- Northwind Business Queries
-- Sprint Day 3 | May 25, 2026
-- Goal: Practice analyst-style SQL queries using
--       real business scenarios and KPI analysis
--
-- Focus Areas:
-- - Revenue analysis
-- - Customer analysis
-- - Product performance
-- - Employee performance
-- - Category contribution
-- - Sales trend analysis
--
-- Key Concepts Practiced:
-- - Joins
-- - Aggregations
-- - GROUP BY
-- - HAVING
-- - Business metrics
-- - Revenue calculations
-- - Analytical thinking
-- ============================================

-- Q1: Who are the top 5 customers by total order value?
/*
Tables needed : customers, orders, order_details
Join path     : customers ON customer_id → orders ON order_id → order_details
Aggregate     : SUM(unit_price * quantity * (1- discount)) AS total_order_value
Filter/Sort   : ORDER BY total_order_value DESC, LIMIT 5
*/
SELECT 
    c.customer_id,
    c.company_name,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_order_value
FROM customers c
JOIN orders o 
    ON c.customer_id = o.customer_id
JOIN order_details od
    ON o.order_id = od.order_id
GROUP BY c.customer_id, c.company_name
ORDER BY total_order_value DESC
LIMIT 5;

-- Q2: Which employee handled the most orders?
/*
Tables needed : orders, employees
Join path     : orders ON employee_id → employee
Aggregate     : COUNT(order_id) AS total_orders_handled
Filter/Sort   : ORDER BY total_orders_handled DESC, LIMIT 1
*/
SELECT
	e.employee_id,
    e.first_name,
    e.last_name,
    COUNT(o.order_id) AS total_orders_handled
FROM orders o 
JOIN employees e 
	ON o.employee_id = e.employee_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY total_orders_handled DESC
LIMIT 1;

-- Q3: What is total revenue per product category?
/*
Tables needed : categories, order_details, products
Join path     : categories ON category_id → products ON product_id → order_details
Aggregate     : SUM(unit_price * quantity * (1- discount)) AS total_revenue
Filter/Sort   : ORDER BY total_revenue DESC
*/
SELECT 
    c.category_id,
    c.category_name,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_revenue
FROM categories c
JOIN products p 
    ON c.category_id = p.category_id
JOIN order_details od
    ON p.product_id = od.product_id
GROUP BY c.category_id, c.category_name
ORDER BY total_revenue DESC;

-- Q4: Which supplier provides the most products in the catalogue?
/*
Tables needed : suppliers, products
Join path     : suppliers ON supplier_id → products
Aggregate     : COUNT(product_id) AS total_products
Filter/Sort   : ORDER BY total_products DESC LIMIT 1
*/
SELECT
	s.supplier_id,
    s.company_name,
    COUNT(p.product_id) AS total_products
FROM suppliers s
JOIN products p 
	ON s.supplier_id = p.supplier_id
GROUP BY s.supplier_id, s.company_name
ORDER BY total_products DESC
LIMIT 1;

-- Q5: Which orders were shipped late or not shipped yet?
/*
Tables needed : orders
Join path     : NA
Aggregate     : NA
Filter/Sort   : NA
*/
SELECT
    order_id,
    customer_id,
    employee_id,
    order_date,
    required_date,
    shipped_date
FROM orders
WHERE shipped_date > required_date
   OR shipped_date IS NULL;


-- Q6: Best Selling Products
SELECT
    p.product_name,
    SUM(od.quantity) AS total_quantity_sold
FROM products p
JOIN order_details od
    ON p.product_id = od.product_id
GROUP BY p.product_name
ORDER BY total_quantity_sold DESC;

-- Q7: Monthly Revenue Trend
SELECT
    YEAR(o.order_date) AS year,
    MONTH(o.order_date) AS month,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_revenue
FROM orders o
JOIN order_details od
    ON o.order_id = od.order_id
GROUP BY
    YEAR(o.order_date),
    MONTH(o.order_date)
ORDER BY
    YEAR(o.order_date),
    MONTH(o.order_date);


-- Q8: Employee Performance
SELECT 
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
FROM employees e
JOIN orders o 
    ON e.employee_id = o.employee_id
JOIN order_details od
    ON o.order_id = od.order_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY total_sales DESC;

-- Q9: Average Order Value
SELECT AVG(t.total_order_value) AS average_order_value
FROM
	(SELECT
		 order_id,
		 SUM(unit_price * quantity * (1 - discount)) AS total_order_value
	 FROM order_details
	 GROUP BY order_id) t;
