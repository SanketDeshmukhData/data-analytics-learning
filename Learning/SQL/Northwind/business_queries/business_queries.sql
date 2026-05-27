-- ============================================
-- Northwind Business Queries
-- Goal: Practice analyst-style SQL queries using
--       real business scenarios and KPI analysis
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
/*
Tables needed : products, order_details
Join path     : products.product_id = order_details.product_id
Aggregate     : SUM(quantity) AS total_quantity_sold
Filter/Sort   : ORDER BY total_quantity_sold DESC
*/
SELECT
    p.product_name,
    SUM(od.quantity) AS total_quantity_sold
FROM products p
JOIN order_details od
    ON p.product_id = od.product_id
GROUP BY p.product_name
ORDER BY total_quantity_sold DESC;


-- Q7: Monthly Revenue Trend
/*
Tables needed : orders, order_details
Join path     : orders.order_id = order_details.order_id
Aggregate     : SUM(unit_price * quantity * (1 - discount)) AS total_revenue
Filter/Sort   : ORDER BY YEAR(order_date), MONTH(order_date)
*/
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
/*
Tables needed : employees, orders, order_details
Join path     : employees.employee_id = orders.employee_id -> orders.order_id = order_details.order_id
Aggregate     : SUM(unit_price * quantity * (1 - discount)) AS total_sales
Filter/Sort   : ORDER BY total_sales DESC
*/
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
/*
Tables needed : order_details
Join path     : NA
Aggregate     : SUM(unit_price * quantity * (1 - discount)) per order -> AVG(order totals)
Filter/Sort   : NA
*/
SELECT AVG(t.total_order_value) AS average_order_value
FROM
	(SELECT
		 order_id,
		 SUM(unit_price * quantity * (1 - discount)) AS total_order_value
	 FROM order_details
	 GROUP BY order_id) t;


-- Q10. Which customers have placed more than 10 orders?
/*
  Business Question : Identifying high frequency customers
  Tables needed     : customers, orders
  Join path         : customers ON customer_id -> orders
  Filter conditions : HAVING total_orders > 10
  Aggregation       : COUNT(order_id) AS total_orders
  Output columns    : company_name, total_orders
*/
SELECT 
	c.company_name,
    COUNT(o.order_id) AS total_orders
FROM customers c 
JOIN orders o 
	ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.company_name
HAVING COUNT(o.order_id) > 10
ORDER BY total_orders DESC;


-- Q11. Which products have never been ordered?
/*
  Business Question : Products that have never been sold for inventory review
  Tables needed     : products, order_details
  Join path         : products ON product_id -> order_details
  Filter conditions : WHERE product_id IS NULL
  Aggregation       : NA
  Output columns    : product_name
*/
SELECT
    p.product_name
FROM products p
LEFT JOIN order_details od
    ON p.product_id = od.product_id
WHERE od.product_id IS NULL;


-- Q12. Which product categories have an average product price above $30?
/*
  Business Question : High value categories for marketing
  Tables needed     : categories, products
  Join path         : categories ON category_id -> products
  Filter conditions : HAVING AVG(unit_price) > 30
  Aggregation       : AVG(unit_price) AS avg_product_price
  Output columns    : category_name, avg_product_price
*/
SELECT
    c.category_name,
    AVG(p.unit_price) AS avg_product_price
FROM categories c
JOIN products p
    ON c.category_id = p.category_id
GROUP BY
    c.category_id,
    c.category_name
HAVING AVG(p.unit_price) > 30;


-- Q13. Which employees have generated more than $100,000 in total sales?
/*
  Business Question : Best performing employees for bonus
  Tables needed     : employees, orders, order_details
  Join path         : employees ON employee_id -> orders ON order_id -> order_details
  Filter conditions : HAVING SUM(unit_price * quantity * (1 - discount)) > 100000
  Aggregation       : SUM(unit_price * quantity * (1 - discount)) AS total_sales
  Output columns    : employee_name, total_sales
*/
SELECT 
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_sales
FROM employees e
JOIN orders o 
    ON e.employee_id = o.employee_id
JOIN order_details od
    ON o.order_id = od.order_id
GROUP BY e.employee_id, e.first_name, e.last_name
HAVING SUM(od.unit_price * od.quantity * (1 - od.discount)) > 100000
ORDER BY total_sales DESC;


-- Q14. What percentage of total revenue does each category contribute?
/*
  Business Question : Finding category-wise distribution for budget allocation
  Tables needed     : categories, products, order_details
  Join path         : categories ON category_id -> products ON product_id -> order_details
  Filter conditions : NA
  Aggregation       : revenue by category / total revenue
  Output columns    : category_name, pct_contribution
*/
SELECT
    c.category_name,
    (
        SUM(od.unit_price * od.quantity * (1 - od.discount))
        /
        (
            SELECT SUM(unit_price * quantity * (1 - discount))
            FROM order_details
        )
    ) * 100.0 AS pct_contribution
FROM categories c
JOIN products p
    ON c.category_id = p.category_id
JOIN order_details od
    ON p.product_id = od.product_id
GROUP BY
    c.category_id, c.category_name
ORDER BY pct_contribution DESC;


-- Q15. What percentage of total orders does each shipper handle?
/*
  Business Question : shipment distribution for logistics
  Tables needed     : shippers, orders
  Join path         : shippers ON shipper_id/ship_via -> orders
  Filter conditions : NA
  Aggregation       : count of shipper id / total no. of orders
  Output columns    : company_name, pct_orders_shipped
*/
SELECT
	s.company_name,
    (
		COUNT(o.ship_via)
        /
        (
			SELECT COUNT(*)
            FROM orders
        )
    ) * 100.0 AS pct_orders_shipped
FROM shippers s
JOIN orders o
	ON s.shipper_id = o.ship_via
GROUP BY s.shipper_id, s.company_name
ORDER BY pct_orders_shipped DESC;


-- Q16. Country Spend Analysis
/*
  Business Question : Identify which countries generate the highest customer activity and revenue for marketing decisions.
  Tables needed     : customers, orders, order_details
  Join path         : customers.customer_id = orders.customer_id -> orders.order_id = order_details.order_id
  Filter conditions : NA
  Aggregation       : COUNT(DISTINCT customer_id), COUNT(DISTINCT order_id), SUM(revenue)
  Output columns    : country, total_customers, total_orders, total_revenue
*/
SELECT 
    c.country,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_revenue
FROM customers c
JOIN orders o 
    ON c.customer_id = o.customer_id
JOIN order_details od
    ON o.order_id = od.order_id
GROUP BY c.country
ORDER BY total_revenue DESC;


-- Q17. Average Shipping Processing Time
/*
  Business Question : Measure average shipping turnaround time by employee and country to identify operational delays and shipping efficiency trends.
  Tables needed     : orders, employees
  Join path         : orders.employee_id = employees.employee_id
  Filter conditions : shipped_date IS NOT NULL
  Aggregation       : AVG(DATEDIFF(shipped_date, order_date)) AS avg_shipping_days
  Output columns    : employee_name, ship_country, avg_shipping_days
*/
SELECT
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    o.ship_country,
    AVG(DATEDIFF(o.shipped_date, o.order_date)) AS avg_shipping_days
FROM orders o
JOIN employees e
    ON o.employee_id = e.employee_id
WHERE o.shipped_date IS NOT NULL
GROUP BY
    employee_name,
    o.ship_country
ORDER BY
    avg_shipping_days DESC;


-- Q18. Customers Above Average Spending
/*
  Business Question : Identify high-value customers for customer targeting and retention strategies.
  Tables needed     : customers, orders, order_details
  Join path         : customers.customer_id = orders.customer_id -> orders.order_id = order_details.order_id
  Filter conditions : customer total spending > average customer spending
  Aggregation       : SUM(revenue) AS total_spending
  Output columns    : company_name, total_spending
*/
SELECT 
    c.company_name,
    SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_spending
FROM customers c
JOIN orders o 
    ON c.customer_id = o.customer_id
JOIN order_details od
    ON o.order_id = od.order_id
GROUP BY c.customer_id, c.company_name
HAVING
	SUM(od.unit_price * od.quantity * (1 - od.discount))
    >
    (
		SELECT AVG(total_spend)
		FROM (
			SELECT 
				SUM(od.unit_price * od.quantity * (1 - od.discount)) AS total_spend
			FROM customers c
			JOIN orders o 
				ON c.customer_id = o.customer_id
			JOIN order_details od
				ON o.order_id = od.order_id
			GROUP BY c.customer_id
		) t
    )
ORDER BY total_spending DESC;