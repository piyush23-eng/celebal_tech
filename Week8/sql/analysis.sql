-- =====================================================================
-- Part 3: SQL Analysis  |  E-Commerce Order Analytics System
-- Target: SQLite 3.25+ (window functions, CTEs, NTILE)
-- Run with: sqlite3 data/ecommerce.db < sql/analysis.sql
-- Or via:   python3 src/run_queries.py   (executes each, saves CSVs)
-- =====================================================================

-- A note on "revenue" throughout this file:
--   revenue = quantity * unit_price * (1 - discount_percent / 100.0)
--   Negative quantity rows are returns and are INCLUDED in this formula
--   on purpose -- a return should subtract from revenue, not be ignored,
--   otherwise "total revenue" would overstate the business.


-- ---------------------------------------------------------------------
-- BASIC QUERIES
-- ---------------------------------------------------------------------

-- 1. Total revenue per category
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 2. Top 10 customers by total order value
SELECT
    c.customer_id,
    c.customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;


-- 3. Month-wise order count for the last 12 months
-- "Last 12 months" is anchored to the latest order_date in the data
-- (not today's system date), so the query stays meaningful for a
-- historical/demo dataset instead of returning zero rows.
WITH anchor AS (
    SELECT MAX(order_date) AS max_date FROM orders
)
SELECT
    strftime('%Y-%m', o.order_date) AS year_month,
    COUNT(*) AS order_count
FROM orders o, anchor
WHERE o.order_date >= date(anchor.max_date, 'start of month', '-11 months')
GROUP BY year_month
ORDER BY year_month;


-- ---------------------------------------------------------------------
-- INTERMEDIATE QUERIES
-- ---------------------------------------------------------------------

-- 4. Customers who placed orders but never had any item delivered
SELECT DISTINCT c.customer_id, c.customer_name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.customer_id NOT IN (
    SELECT o2.customer_id
    FROM orders o2
    WHERE o2.status = 'DELIVERED' AND o2.customer_id IS NOT NULL
);


-- 5. Products that were ordered but had more returns than purchases
-- "purchases" = rows with positive quantity, "returns" = rows with negative quantity
SELECT
    p.product_id,
    p.product_name,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS units_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS units_returned
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
HAVING units_returned > units_purchased;


-- 6. Return rate (returned items / total items) per category
SELECT
    p.category,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS returned_units,
    SUM(ABS(oi.quantity)) AS total_units,
    ROUND(
        1.0 * SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END)
        / SUM(ABS(oi.quantity)), 4
    ) AS return_rate
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY return_rate DESC;


-- ---------------------------------------------------------------------
-- ADVANCED QUERIES (Window Functions, CTEs, Subqueries)
-- ---------------------------------------------------------------------

-- 7. Running total of revenue per region, ordered by date
WITH daily AS (
    SELECT
        o.region_code,
        date(o.order_date) AS order_day,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.region_code, order_day
)
SELECT
    region_code,
    order_day AS order_date,
    ROUND(daily_revenue, 2) AS daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code ORDER BY order_day
    ), 2) AS running_total
FROM daily
ORDER BY region_code, order_day;


-- 8. Rank products by total revenue within each category (DENSE_RANK, ties share rank)
WITH product_revenue AS (
    SELECT
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_name
)
SELECT
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;


-- 9. Days between consecutive orders per customer (LAG), flag "At Risk" if avg gap > 30 days
WITH customer_orders AS (
    SELECT
        customer_id,
        date(order_date) AS order_date
    FROM orders
    WHERE customer_id IS NOT NULL
),
gaps AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date,
        julianday(order_date) - julianday(
            LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)
        ) AS days_gap
    FROM customer_orders
),
avg_gap AS (
    SELECT customer_id, AVG(days_gap) AS avg_days_gap
    FROM gaps
    WHERE days_gap IS NOT NULL
    GROUP BY customer_id
)
SELECT
    g.customer_id,
    g.order_date,
    g.previous_order_date,
    g.days_gap,
    CASE WHEN a.avg_days_gap > 30 THEN 'At Risk' ELSE 'Healthy' END AS risk_flag
FROM gaps g
JOIN avg_gap a ON a.customer_id = g.customer_id
ORDER BY g.customer_id, g.order_date;


-- 10. Multi-level CTE: monthly revenue per customer -> High/Medium/Low -> counts per month
WITH monthly_revenue AS (
    SELECT
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS year_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id, year_month
),
categorized AS (
    SELECT
        customer_id,
        year_month,
        revenue,
        CASE
            WHEN revenue > 10000 THEN 'High'
            WHEN revenue >= 5000 THEN 'Medium'
            ELSE 'Low'
        END AS revenue_category
    FROM monthly_revenue
)
SELECT
    year_month,
    revenue_category,
    COUNT(DISTINCT customer_id) AS customer_count
FROM categorized
GROUP BY year_month, revenue_category
ORDER BY year_month, revenue_category;


-- 11. NTILE: divide customers into 4 quartiles by lifetime value
WITH customer_value AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    ROUND(total_value, 2) AS total_value,
    NTILE(4) OVER (ORDER BY total_value DESC) AS quartile,
    CASE NTILE(4) OVER (ORDER BY total_value DESC)
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS quartile_label
FROM customer_value
ORDER BY total_value DESC;


-- 12. Year-over-year comparison per month
WITH monthly AS (
    SELECT
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS year,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY year, month
)
SELECT
    m.year,
    m.month,
    ROUND(m.revenue, 2) AS revenue,
    ROUND(p.revenue, 2) AS prev_year_revenue,
    CASE
        WHEN p.revenue IS NULL OR p.revenue = 0 THEN NULL
        ELSE ROUND(100.0 * (m.revenue - p.revenue) / p.revenue, 2)
    END AS yoy_growth_percent
FROM monthly m
LEFT JOIN monthly p ON p.year = m.year - 1 AND p.month = m.month
ORDER BY m.year, m.month;


-- 13. First / last purchased category per customer, flag category_shift
WITH ordered_purchases AS (
    SELECT
        o.customer_id,
        o.order_date,
        p.category,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC)  AS rn_first,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC) AS rn_last
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.customer_id IS NOT NULL
),
first_cat AS (SELECT customer_id, category AS first_category FROM ordered_purchases WHERE rn_first = 1),
last_cat  AS (SELECT customer_id, category AS last_category  FROM ordered_purchases WHERE rn_last  = 1)
SELECT
    f.customer_id,
    f.first_category,
    l.last_category,
    CASE WHEN f.first_category <> l.last_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM first_cat f
JOIN last_cat l ON l.customer_id = f.customer_id
ORDER BY f.customer_id;


-- 14. Cumulative distribution: % of total revenue from top N% of customers
WITH customer_value AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),
ranked AS (
    SELECT
        customer_id,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
        SUM(revenue) OVER ()                       AS grand_total
    FROM customer_value
)
SELECT
    customer_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND(100.0 * cumulative_revenue / grand_total, 2) AS cumulative_percent
FROM ranked
ORDER BY revenue DESC;


-- 15. Cohort analysis: registration-month cohorts, retention in months 0-3
WITH cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_orders AS (
    SELECT
        o.customer_id,
        c.cohort_month,
        (
            (CAST(strftime('%Y', o.order_date) AS INT) - CAST(strftime('%Y', c.cohort_month || '-01') AS INT)) * 12
            + (CAST(strftime('%m', o.order_date) AS INT) - CAST(strftime('%m', c.cohort_month || '-01') AS INT))
        ) AS month_offset
    FROM orders o
    JOIN cohort c ON c.customer_id = o.customer_id
    WHERE o.customer_id IS NOT NULL
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM cohort
    GROUP BY cohort_month
),
activity AS (
    SELECT
        cohort_month,
        month_offset,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM customer_orders
    WHERE month_offset BETWEEN 0 AND 3
    GROUP BY cohort_month, month_offset
)
SELECT
    a.cohort_month,
    a.month_offset,
    a.active_customers,
    s.cohort_customers,
    ROUND(100.0 * a.active_customers / s.cohort_customers, 2) AS retention_rate_percent
FROM activity a
JOIN cohort_size s ON s.cohort_month = a.cohort_month
ORDER BY a.cohort_month, a.month_offset;


-- 16. Self-join: products frequently bought together (same order, A-B pair once)
SELECT
    pa.product_name AS product_a,
    pb.product_name AS product_b,
    COUNT(*) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2
    ON oi1.order_id = oi2.order_id
    AND oi1.product_id < oi2.product_id      -- forces A-B and never B-A / A-A
JOIN products pa ON pa.product_id = oi1.product_id
JOIN products pb ON pb.product_id = oi2.product_id
GROUP BY pa.product_name, pb.product_name
HAVING COUNT(*) > 1
ORDER BY times_bought_together DESC
LIMIT 25;
