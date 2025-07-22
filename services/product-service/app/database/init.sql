CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE retailers (
    retailer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    provides_rating BOOLEAN DEFAULT FALSE,
    scraping_config JSONB
);

CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id INT REFERENCES retailers(retailer_id),
    external_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    current_price NUMERIC,
    category VARCHAR(100) CHECK (category IN ('fruit', 'vegetable', 'dairy', 'poultry', 'bakery', 'others')),
    brand VARCHAR(100),
    size_description VARCHAR(100),
    base_quantity NUMERIC,
    base_unit VARCHAR(20),
    image_url VARCHAR(255),
    product_url VARCHAR(255) NOT NULL,
    rating NUMERIC(3,2), 
    badges JSONB,
    currency CHAR(3) DEFAULT 'GBP',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(retailer_id, external_id)
);

CREATE TABLE price_history (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(product_id),
    price NUMERIC(8,2) NOT NULL,
    unit_price NUMERIC(8,2), -- Normalized price per base unit
    is_offer BOOLEAN DEFAULT FALSE,
    offer_description TEXT,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- For price predictions
CREATE TABLE price_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(product_id),
    predicted_price NUMERIC(8,2) NOT NULL,
    confidence_lower NUMERIC(8,2),
    confidence_upper NUMERIC(8,2),
    prediction_date DATE NOT NULL,
    algorithm_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_products_name ON products USING gin(name gin_trgm_ops);
CREATE INDEX idx_price_history_product ON price_history(product_id, timestamp);



INSERT INTO retailers (name, base_url, provides_rating)
SELECT 'Sainsbury', 'https://www.sainsburys.co.uk', true
WHERE NOT EXISTS (SELECT 1 FROM retailers WHERE name = 'Sainsbury');

INSERT INTO retailers (name, base_url, provides_rating)
SELECT 'Iceland', 'https://www.iceland.co.uk', true
WHERE NOT EXISTS (SELECT 1 FROM retailers WHERE name = 'Iceland');

INSERT INTO retailers (name, base_url, provides_rating)
SELECT 'Morrisons', 'https://groceries.morrisons.com', true
WHERE NOT EXISTS (SELECT 1 FROM retailers WHERE name = 'Morrisons');

INSERT INTO retailers (name, base_url, provides_rating)
SELECT 'Aldi', 'https://groceries.aldi.co.uk', false
WHERE NOT EXISTS (SELECT 1 FROM retailers WHERE name = 'Aldi');
