CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS dim_producto (
    sku VARCHAR(80) PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(120),
    style VARCHAR(120),
    size VARCHAR(40),
    asin VARCHAR(40)
);

ALTER TABLE dim_producto ADD COLUMN IF NOT EXISTS name VARCHAR(255);
ALTER TABLE dim_producto ADD COLUMN IF NOT EXISTS category VARCHAR(120);
ALTER TABLE dim_producto ADD COLUMN IF NOT EXISTS style VARCHAR(120);
ALTER TABLE dim_producto ADD COLUMN IF NOT EXISTS size VARCHAR(40);
ALTER TABLE dim_producto ADD COLUMN IF NOT EXISTS asin VARCHAR(40);

CREATE TABLE IF NOT EXISTS dim_cliente (
    cliente_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    b2b BOOLEAN,
    customer_nk VARCHAR(30)
);

ALTER TABLE dim_cliente ADD COLUMN IF NOT EXISTS b2b BOOLEAN;
ALTER TABLE dim_cliente ADD COLUMN IF NOT EXISTS customer_nk VARCHAR(30);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dim_cliente_customer_nk
    ON dim_cliente (customer_nk);

CREATE TABLE IF NOT EXISTS dim_envio (
    id_envio UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(120),
    fulfillment VARCHAR(80),
    sales_chanel VARCHAR(80),
    ship_service_level VARCHAR(80),
    ship_city VARCHAR(120),
    ship_state VARCHAR(120),
    ship_postal_code VARCHAR(20),
    ship_country VARCHAR(20),
    shipping_nk VARCHAR(500),
    courier_status VARCHAR(120),
    fulfilled_by VARCHAR(80)
);

ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS status VARCHAR(120);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS fulfillment VARCHAR(80);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS sales_chanel VARCHAR(80);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS ship_service_level VARCHAR(80);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS ship_city VARCHAR(120);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS ship_state VARCHAR(120);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS ship_postal_code VARCHAR(20);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS ship_country VARCHAR(20);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS shipping_nk VARCHAR(500);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS courier_status VARCHAR(120);
ALTER TABLE dim_envio ADD COLUMN IF NOT EXISTS fulfilled_by VARCHAR(80);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dim_envio_shipping_nk
    ON dim_envio (shipping_nk);

CREATE TABLE IF NOT EXISTS dim_tiempo (
    date DATE PRIMARY KEY,
    day INT,
    week INT,
    month INT,
    trimester INT,
    year INT,
    month_name VARCHAR(20)
);

ALTER TABLE dim_tiempo ADD COLUMN IF NOT EXISTS day INT;
ALTER TABLE dim_tiempo ADD COLUMN IF NOT EXISTS week INT;
ALTER TABLE dim_tiempo ADD COLUMN IF NOT EXISTS month INT;
ALTER TABLE dim_tiempo ADD COLUMN IF NOT EXISTS trimester INT;
ALTER TABLE dim_tiempo ADD COLUMN IF NOT EXISTS year INT;
ALTER TABLE dim_tiempo ADD COLUMN IF NOT EXISTS month_name VARCHAR(20);

CREATE TABLE IF NOT EXISTS fact_ventas (
    id_venta UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(80) REFERENCES dim_producto(sku),
    cliente_id UUID REFERENCES dim_cliente(cliente_id),
    id_envio UUID REFERENCES dim_envio(id_envio),
    date DATE REFERENCES dim_tiempo(date),
    quantity INT,
    amount DECIMAL(12, 2),
    ticket_promedio DECIMAL(12, 2),
    source_row_id INT,
    order_id VARCHAR(40),
    currency VARCHAR(10)
);

ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS sku VARCHAR(80);
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS cliente_id UUID;
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS id_envio UUID;
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS date DATE;
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS quantity INT;
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS amount DECIMAL(12, 2);
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS ticket_promedio DECIMAL(12, 2);
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS source_row_id INT;
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS order_id VARCHAR(40);
ALTER TABLE fact_ventas ADD COLUMN IF NOT EXISTS currency VARCHAR(10);

CREATE UNIQUE INDEX IF NOT EXISTS idx_fact_ventas_source_row_id
    ON fact_ventas (source_row_id);

CREATE INDEX IF NOT EXISTS idx_fact_ventas_date
    ON fact_ventas (date);

