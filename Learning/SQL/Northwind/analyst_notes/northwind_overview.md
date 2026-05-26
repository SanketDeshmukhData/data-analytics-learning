# Northwind Database Overview

## Purpose of Database

The Northwind database represents a fictional trading company that manages:
- customers
- products
- suppliers
- employees
- orders
- shipping operations

It is widely used for practicing SQL, business analysis, and analytical thinking because it simulates a realistic sales environment.

The database helps understand:
- transactional data
- relational database structure
- business KPIs
- reporting logic
- analytical workflows

---

# Core Business Flow

The overall sales process follows this flow:
```
Customer
↓
Orders
↓
Order Details
↓
Products
↓
Categories / Suppliers
↓
Shipping
```
This represents how a customer order moves through the business system.

---

# Main Tables

## customers

Stores customer information.

### Important Columns
- customer_id
- company_name
- contact_name
- city
- country

### Business Meaning
Represents companies or buyers placing orders.

---

## orders

Stores order-level transaction information.

### Important Columns
- order_id
- customer_id
- employee_id
- order_date
- ship_via

### Business Meaning
Represents a single customer transaction.

Each order belongs to:
- one customer
- one employee
- one shipper

---

## order_details

Stores product-level details inside each order.

### Important Columns
- order_id
- product_id
- quantity
- unit_price
- discount

### Business Meaning
Represents individual line items inside an order.

This is one of the most important tables because:
- revenue is calculated here
- quantities sold are stored here
- product performance analysis starts here

---

## products

Stores product information.

### Important Columns
- product_id
- product_name
- supplier_id
- category_id
- unit_price

### Business Meaning
Represents items sold to customers.

Each product belongs to:
- one category
- one supplier

---

## categories

Stores product category information.

### Important Columns
- category_id
- category_name

### Business Meaning
Used to group products into business segments.

Examples:
- beverages
- seafood
- dairy products

---

## suppliers

Stores supplier/vendor information.

### Important Columns
- supplier_id
- company_name
- country

### Business Meaning
Represents companies supplying products to Northwind.

---

## employees

Stores employee information.

### Important Columns
- employee_id
- first_name
- last_name
- title

### Business Meaning
Represents employees handling customer orders.

Used for:
- sales analysis
- employee performance analysis

---

## shippers

Stores shipping company information.

### Important Columns
- shipper_id
- company_name

### Business Meaning
Represents logistics/shipping providers delivering customer orders.

---

# Important Relationships

| Parent Table | Child Table | Relationship |
|---|---|---|
| customers | orders | One-to-Many |
| employees | orders | One-to-Many |
| shippers | orders | One-to-Many |
| orders | order_details | One-to-Many |
| products | order_details | One-to-Many |
| categories | products | One-to-Many |
| suppliers | products | One-to-Many |

---

# Revenue Logic

Revenue is calculated at the `order_details` level.

Basic formula:

```sql
quantity * unit_price
```

If discounts are included:

```sql
(quantity * unit_price) * (1 - discount)
```

Important:
Revenue should not be calculated directly from the `orders` table because:
- orders do not contain product quantities
- orders do not contain line-item pricing

---

# Granularity Notes

Understanding granularity is extremely important in analytics.

## orders Table

One row represents:
- one customer order

This is called:
Order-Level Granularity

---

## order_details Table

One row represents:
- one product inside one order

This is called:
Line-Item Granularity

Example:

One order may contain:
- 3 products
- 5 products
- 10 products

Therefore:
- one order can have multiple rows in order_details

This distinction is important for:
- aggregations
- revenue calculations
- joins
- KPI analysis

---

# Business Analysis Possibilities

The Northwind database can be used for multiple analytical scenarios.

---

## Customer Analysis

Examples:
- top customers by revenue
- customer purchase frequency
- country-wise customer analysis

---

## Product Analysis

Examples:
- best-selling products
- highest revenue products
- low-performing products

---

## Category Analysis

Examples:
- category-wise revenue contribution
- category sales trends
- category performance comparison

---

## Employee Analysis

Examples:
- employee sales performance
- number of orders handled
- revenue managed by employee

---

## Time-Series Analysis

Examples:
- monthly sales trends
- yearly revenue growth
- seasonal sales patterns

---

## Shipping Analysis

Examples:
- orders handled by shipping companies
- shipment distribution analysis

---

# Key Analytical Concepts Learned

The Northwind database helps practice:

- joins
- aggregations
- GROUP BY and HAVING
- subqueries
- correlated subqueries
- CTEs
- window functions
- KPI calculations
- business logic decomposition
- analytical thinking

---

# Key Learning Outcome

The main goal of working with Northwind is not just writing SQL queries.

It is learning how to:
- think like a data analyst
- understand business processes
- connect tables logically
- calculate meaningful metrics
- solve business problems using data