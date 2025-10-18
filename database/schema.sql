-- ============================================================================
-- E-Commerce Analytics Star Schema
-- Dimensional Data Model for Sales Performance Analytics
-- ============================================================================

-- Drop existing tables
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS fact_returns CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;
DROP TABLE IF EXISTS dim_geography CASCADE;
DROP TABLE IF EXISTS dim_marketing_campaigns CASCADE;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- Dimension: Customers
CREATE TABLE dim_customers (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    registration_date DATE,
    customer_segment VARCHAR(20),
    age INTEGER,
    gender VARCHAR(20),
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_segment ON dim_customers(customer_segment);
CREATE INDEX idx_customers_reg_date ON dim_customers(registration_date);


-- Dimension: Products
CREATE TABLE dim_products (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(20) UNIQUE NOT NULL,
    product_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    weight_kg DECIMAL(10, 2),
    stock_quantity INTEGER,
    rating DECIMAL(3, 1),
    num_reviews INTEGER,
    launch_date DATE,
    -- Calculated
    margin_amount DECIMAL(10, 2) GENERATED ALWAYS AS (price - cost) STORED,
    margin_percent DECIMAL(5, 2) GENERATED ALWAYS AS ((price - cost) / NULLIF(price, 0) * 100) STORED,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON dim_products(category);
CREATE INDEX idx_products_price ON dim_products(price);
CREATE INDEX idx_products_rating ON dim_products(rating);


-- Dimension: Time
CREATE TABLE dim_time (
    time_key SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN DEFAULT FALSE,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER
);

CREATE INDEX idx_time_date ON dim_time(date);
CREATE INDEX idx_time_year_month ON dim_time(year, month);
CREATE INDEX idx_time_quarter ON dim_time(year, quarter);


-- Dimension: Geography
CREATE TABLE dim_geography (
    geography_key SERIAL PRIMARY KEY,
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    zip_code VARCHAR(20),
    region VARCHAR(100),
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country, state, city, zip_code)
);

CREATE INDEX idx_geography_country ON dim_geography(country);
CREATE INDEX idx_geography_state ON dim_geography(state);


-- Dimension: Marketing Campaigns
CREATE TABLE dim_marketing_campaigns (
    campaign_key SERIAL PRIMARY KEY,
    campaign_id VARCHAR(20) UNIQUE NOT NULL,
    campaign_name VARCHAR(255),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2),
    channel VARCHAR(50),
    target_segment VARCHAR(50),
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    -- Calculated metrics
    click_through_rate DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE WHEN impressions > 0 THEN (clicks::DECIMAL / impressions * 100) ELSE 0 END
    ) STORED,
    conversion_rate DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE WHEN clicks > 0 THEN (conversions::DECIMAL / clicks * 100) ELSE 0 END
    ) STORED,
    cost_per_click DECIMAL(10, 2) GENERATED ALWAYS AS (
        CASE WHEN clicks > 0 THEN (budget / clicks) ELSE 0 END
    ) STORED,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_dates ON dim_marketing_campaigns(start_date, end_date);


-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- Fact: Sales Transactions
CREATE TABLE fact_sales (
    sales_key SERIAL PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    
    -- Foreign Keys to Dimensions
    customer_key INTEGER REFERENCES dim_customers(customer_key),
    product_key INTEGER REFERENCES dim_products(product_key),
    time_key INTEGER REFERENCES dim_time(time_key),
    geography_key INTEGER REFERENCES dim_geography(geography_key),
    
    -- Transaction Details
    transaction_date DATE NOT NULL,
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    
    -- Financial Measures
    subtotal DECIMAL(12, 2),
    discount_percent DECIMAL(5, 2),
    discount_amount DECIMAL(10, 2),
    tax_amount DECIMAL(10, 2),
    shipping_cost DECIMAL(10, 2),
    total_amount DECIMAL(12, 2),
    
    -- Additional Attributes
    payment_method VARCHAR(50),
    order_status VARCHAR(50),
    shipping_address TEXT,
    order_notes TEXT,
    
    -- Calculated Measures
    net_revenue DECIMAL(12, 2) GENERATED ALWAYS AS (total_amount - COALESCE(discount_amount, 0)) STORED,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_transaction_id ON fact_sales(transaction_id);
CREATE INDEX idx_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_sales_product ON fact_sales(product_key);
CREATE INDEX idx_sales_time ON fact_sales(time_key);
CREATE INDEX idx_sales_date ON fact_sales(transaction_date);
CREATE INDEX idx_sales_status ON fact_sales(order_status);
CREATE INDEX idx_sales_payment ON fact_sales(payment_method);

-- Composite indexes for common queries
CREATE INDEX idx_sales_customer_date ON fact_sales(customer_key, transaction_date);
CREATE INDEX idx_sales_product_date ON fact_sales(product_key, transaction_date);


-- Fact: Returns
CREATE TABLE fact_returns (
    return_key SERIAL PRIMARY KEY,
    return_id VARCHAR(20) UNIQUE NOT NULL,
    
    -- Foreign Keys
    sales_key INTEGER REFERENCES fact_sales(sales_key),
    customer_key INTEGER REFERENCES dim_customers(customer_key),
    product_key INTEGER REFERENCES dim_products(product_key),
    return_time_key INTEGER REFERENCES dim_time(time_key),
    
    -- Return Details
    transaction_id VARCHAR(30) NOT NULL,
    return_date DATE NOT NULL,
    return_reason VARCHAR(255),
    refund_amount DECIMAL(12, 2),
    return_status VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_returns_transaction ON fact_returns(transaction_id);
CREATE INDEX idx_returns_customer ON fact_returns(customer_key);
CREATE INDEX idx_returns_product ON fact_returns(product_key);
CREATE INDEX idx_returns_date ON fact_returns(return_date);
CREATE INDEX idx_returns_reason ON fact_returns(return_reason);


-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Sales Overview with all dimensions
CREATE OR REPLACE VIEW vw_sales_overview AS
SELECT 
    fs.sales_key,
    fs.transaction_id,
    fs.transaction_date,
    
    -- Customer Dimensions
    dc.customer_id,
    dc.first_name || ' ' || dc.last_name AS customer_name,
    dc.customer_segment,
    dc.age,
    dc.gender,
    
    -- Product Dimensions
    dp.product_id,
    dp.product_name,
    dp.category,
    dp.subcategory,
    dp.brand,
    dp.margin_percent,
    
    -- Time Dimensions
    dt.year,
    dt.quarter,
    dt.month,
    dt.month_name,
    dt.week,
    dt.day_name,
    dt.is_weekend,
    
    -- Geography Dimensions
    dg.country,
    dg.state,
    dg.city,
    
    -- Measures
    fs.quantity,
    fs.unit_price,
    fs.subtotal,
    fs.discount_amount,
    fs.tax_amount,
    fs.shipping_cost,
    fs.total_amount,
    fs.net_revenue,
    fs.payment_method,
    fs.order_status,
    
    -- Calculated Measures
    dp.cost * fs.quantity AS total_cost,
    (fs.total_amount - (dp.cost * fs.quantity)) AS profit
FROM fact_sales fs
LEFT JOIN dim_customers dc ON fs.customer_key = dc.customer_key
LEFT JOIN dim_products dp ON fs.product_key = dp.product_key
LEFT JOIN dim_time dt ON fs.time_key = dt.time_key
LEFT JOIN dim_geography dg ON fs.geography_key = dg.geography_key;


-- Customer Lifetime Value View
CREATE OR REPLACE VIEW vw_customer_lifetime_value AS
SELECT 
    dc.customer_id,
    dc.customer_segment,
    dc.registration_date,
    COUNT(DISTINCT fs.transaction_id) AS total_transactions,
    SUM(fs.total_amount) AS total_revenue,
    AVG(fs.total_amount) AS avg_transaction_value,
    MAX(fs.transaction_date) AS last_purchase_date,
    MIN(fs.transaction_date) AS first_purchase_date,
    (CURRENT_DATE - MAX(fs.transaction_date)) AS days_since_last_purchase,
    (MAX(fs.transaction_date) - MIN(fs.transaction_date)) AS customer_lifetime_days
FROM dim_customers dc
LEFT JOIN fact_sales fs ON dc.customer_key = fs.customer_key
WHERE fs.order_status = 'Completed'
GROUP BY dc.customer_id, dc.customer_segment, dc.registration_date;


-- Product Performance View
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT 
    dp.product_id,
    dp.product_name,
    dp.category,
    dp.brand,
    dp.price,
    COUNT(fs.transaction_id) AS total_orders,
    SUM(fs.quantity) AS total_units_sold,
    SUM(fs.total_amount) AS total_revenue,
    AVG(fs.total_amount) AS avg_order_value,
    SUM(fs.total_amount - (dp.cost * fs.quantity)) AS total_profit,
    AVG(fs.total_amount - (dp.cost * fs.quantity)) AS avg_profit_per_order
FROM dim_products dp
LEFT JOIN fact_sales fs ON dp.product_key = fs.product_key
WHERE fs.order_status = 'Completed'
GROUP BY dp.product_id, dp.product_name, dp.category, dp.brand, dp.price, dp.cost;


-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to populate time dimension
CREATE OR REPLACE FUNCTION populate_time_dimension(start_date DATE, end_date DATE)
RETURNS VOID AS $$
DECLARE
    current_date DATE := start_date;
BEGIN
    WHILE current_date <= end_date LOOP
        INSERT INTO dim_time (
            date, year, quarter, month, month_name, week,
            day_of_month, day_of_week, day_name, is_weekend,
            fiscal_year, fiscal_quarter
        ) VALUES (
            current_date,
            EXTRACT(YEAR FROM current_date),
            EXTRACT(QUARTER FROM current_date),
            EXTRACT(MONTH FROM current_date),
            TO_CHAR(current_date, 'Month'),
            EXTRACT(WEEK FROM current_date),
            EXTRACT(DAY FROM current_date),
            EXTRACT(DOW FROM current_date),
            TO_CHAR(current_date, 'Day'),
            EXTRACT(DOW FROM current_date) IN (0, 6),
            EXTRACT(YEAR FROM current_date),
            EXTRACT(QUARTER FROM current_date)
        ) ON CONFLICT (date) DO NOTHING;
        
        current_date := current_date + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Populate time dimension for 2022-2024
SELECT populate_time_dimension('2022-01-01', '2024-12-31');


-- ============================================================================
-- GRANTS (adjust based on your user setup)
-- ============================================================================

-- Grant permissions (uncomment and adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO analytics_user;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA public TO analytics_user;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'E-Commerce Analytics Schema Created!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Dimension Tables: 5';
    RAISE NOTICE 'Fact Tables: 2';
    RAISE NOTICE 'Views: 3';
    RAISE NOTICE 'Ready for data loading!';
    RAISE NOTICE '========================================';
END $$;



