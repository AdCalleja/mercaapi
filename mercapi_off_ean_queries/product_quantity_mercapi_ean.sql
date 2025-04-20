-- Drop table if exists
DROP TABLE IF EXISTS product_quantity_off;

-- Create product_quantity_off table from mercadona_ean_products_robust
CREATE TABLE IF NOT EXISTS product_quantity_off AS
SELECT 
    json_extract_string(json, '$.code') AS ean,
    json_extract_string(json, '$.quantity') AS quantity,
    TRY_CAST(json_extract_string(json, '$.product_quantity') AS FLOAT) AS product_quantity,
    json_extract_string(json, '$.product_quantity_unit') AS product_quantity_unit
FROM mercadona_ean_products_robust;

-- Add primary key to ean column
ALTER TABLE product_quantity_off ADD PRIMARY KEY (ean);

-- Export product_quantity_off table to CSV
COPY product_quantity_off TO '/home/adrian/code/mercaapi/product_quantity_off.csv' (HEADER, DELIMITER ','); 