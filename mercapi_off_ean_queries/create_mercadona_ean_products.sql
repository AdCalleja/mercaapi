-- SQL query to create mercadona_ean_products table
-- Filters Open Food Facts data with EAN list from CSV
-- Handles various EAN formats including leading/trailing zeros

CREATE TABLE mercadona_ean_products AS
WITH csv_eans AS (
    SELECT ean FROM read_csv('/home/adrian/code/mercaapi/mercapi_ean.csv', auto_detect=TRUE)
),
standardized_eans AS (
    -- Create multiple formats of each EAN to match against
    SELECT 
        ean AS original_ean,
        ean AS standard_ean,
        '"' || ean || '"' AS quoted_ean,
        -- For EANs stored as numbers (potential leading zeros lost)
        CASE 
            WHEN LENGTH(CAST(ean AS VARCHAR)) < 13 AND TRY_CAST(ean AS BIGINT) IS NOT NULL 
            THEN LPAD(CAST(ean AS VARCHAR), 13, '0') 
            ELSE CAST(ean AS VARCHAR) 
        END AS padded_ean,
        '"' || CASE 
            WHEN LENGTH(CAST(ean AS VARCHAR)) < 13 AND TRY_CAST(ean AS BIGINT) IS NOT NULL 
            THEN LPAD(CAST(ean AS VARCHAR), 13, '0') 
            ELSE CAST(ean AS VARCHAR) 
        END || '"' AS quoted_padded_ean,
        -- For cases where quotes or formatting is inconsistent
        REPLACE(CAST(ean AS VARCHAR), '"', '') AS unquoted_ean,
        -- For trailing zeros that might have been trimmed
        RTRIM(CAST(ean AS VARCHAR), '0') AS trimmed_ean,
        '"' || RTRIM(CAST(ean AS VARCHAR), '0') || '"' AS quoted_trimmed_ean
    FROM csv_eans
)

SELECT json.* 
FROM read_ndjson('/home/adrian/code/open_food_facts/openfoodfacts-products.jsonl.gz', ignore_errors=True) as json
WHERE 
    json.code IN (SELECT standard_ean FROM standardized_eans)
    OR json.code IN (SELECT quoted_ean FROM standardized_eans)
    OR json.code IN (SELECT padded_ean FROM standardized_eans) 
    OR json.code IN (SELECT quoted_padded_ean FROM standardized_eans)
    OR json.code IN (SELECT unquoted_ean FROM standardized_eans)
    OR json.code IN (SELECT trimmed_ean FROM standardized_eans)
    OR json.code IN (SELECT quoted_trimmed_ean FROM standardized_eans)
    -- Also try matching against the id field which sometimes contains the clean EAN
    OR json._id IN (SELECT standard_ean FROM standardized_eans)
    OR json._id IN (SELECT quoted_ean FROM standardized_eans)
    OR json._id IN (SELECT padded_ean FROM standardized_eans)
    OR json._id IN (SELECT unquoted_ean FROM standardized_eans); 