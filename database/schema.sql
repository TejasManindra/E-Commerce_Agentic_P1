-- ============================================
-- E-Commerce Agentic BI Database Schema
-- ============================================

DROP TABLE IF EXISTS delivery CASCADE;
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS marketing_campaigns CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS targets CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;


-- ============================================
-- CUSTOMERS
-- ============================================

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(150),
    gender VARCHAR(20),
    age INTEGER,
    city VARCHAR(100),
    state VARCHAR(100),
    customer_segment VARCHAR(50),
    acquisition_channel VARCHAR(100),
    registration_date DATE
);


-- ============================================
-- PRODUCTS
-- ============================================

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    selling_price NUMERIC(12,2),
    cost_price NUMERIC(12,2),
    launch_date DATE
);


-- ============================================
-- ORDERS
-- ============================================

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_date DATE,
    channel VARCHAR(50),
    payment_method VARCHAR(50),
    order_status VARCHAR(50),
    shipping_state VARCHAR(100),
    shipping_city VARCHAR(100),
    subtotal NUMERIC(12,2),
    discount_amount NUMERIC(12,2),
    shipping_fee NUMERIC(12,2),
    tax_amount NUMERIC(12,2),
    total_amount NUMERIC(12,2),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- ============================================
-- ORDER ITEMS
-- ============================================

CREATE TABLE order_items (
    order_item_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INTEGER,
    unit_price NUMERIC(12,2),
    discount_percent NUMERIC(8,2),
    cost_price NUMERIC(12,2),
    revenue NUMERIC(12,2),
    cost NUMERIC(12,2),
    profit NUMERIC(12,2),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


-- ============================================
-- MARKETING CAMPAIGNS
-- ============================================

CREATE TABLE marketing_campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_date DATE,
    channel VARCHAR(100),
    campaign_name VARCHAR(200),
    spend NUMERIC(12,2),
    impressions BIGINT,
    clicks BIGINT,
    conversions INTEGER,
    revenue_generated NUMERIC(12,2),
    new_customers INTEGER
);


-- ============================================
-- RETURNS
-- ============================================

CREATE TABLE returns (
    return_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    customer_id VARCHAR(50),
    return_date DATE,
    return_reason VARCHAR(150),
    return_quantity INTEGER,
    refund_amount NUMERIC(12,2),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- ============================================
-- PAYMENTS
-- ============================================

CREATE TABLE payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    payment_date DATE,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    amount NUMERIC(12,2),
    failure_reason VARCHAR(200),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- ============================================
-- INVENTORY
-- ============================================

CREATE TABLE inventory (
    inventory_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50),
    date DATE,
    opening_stock INTEGER,
    units_received INTEGER,
    units_sold INTEGER,
    closing_stock INTEGER,
    reorder_level INTEGER,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


-- ============================================
-- DELIVERY
-- ============================================

CREATE TABLE delivery (
    delivery_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    courier VARCHAR(100),
    shipped_date DATE,
    delivered_date DATE,
    expected_delivery_date DATE,
    delivery_status VARCHAR(50),
    shipping_cost NUMERIC(12,2),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- ============================================
-- TARGETS
-- ============================================

CREATE TABLE targets (
    target_id VARCHAR(50) PRIMARY KEY,
    month DATE,
    revenue_target NUMERIC(12,2),
    profit_target NUMERIC(12,2),
    orders_target INTEGER,
    customer_target INTEGER
);