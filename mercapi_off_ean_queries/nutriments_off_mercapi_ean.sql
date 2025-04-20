-- Drop table if exists
DROP TABLE IF EXISTS nutriments_off;

-- Create nutriments_off table from mercadona_ean_products_robust with individual columns
CREATE TABLE IF NOT EXISTS nutriments_off AS
SELECT 
    json_extract_string(json, '$.code') AS ean,
    TRY_CAST(json_extract_string(json, '$.nutriments.energy-kj') AS FLOAT) AS energy_kj,
    TRY_CAST(json_extract_string(json, '$.nutriments.energy-kj_100g') AS FLOAT) AS energy_kj_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.energy-kcal') AS FLOAT) AS energy_kcal,
    TRY_CAST(json_extract_string(json, '$.nutriments.energy-kcal_100g') AS FLOAT) AS energy_kcal_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.fat') AS FLOAT) AS fat,
    TRY_CAST(json_extract_string(json, '$.nutriments.fat_100g') AS FLOAT) AS fat_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.saturated-fat') AS FLOAT) AS saturated_fat,
    TRY_CAST(json_extract_string(json, '$.nutriments.saturated-fat_100g') AS FLOAT) AS saturated_fat_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.monounsaturated-fat') AS FLOAT) AS monounsaturated_fat,
    TRY_CAST(json_extract_string(json, '$.nutriments.monounsaturated-fat_100g') AS FLOAT) AS monounsaturated_fat_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.polyunsaturated-fat') AS FLOAT) AS polyunsaturated_fat,
    TRY_CAST(json_extract_string(json, '$.nutriments.polyunsaturated-fat_100g') AS FLOAT) AS polyunsaturated_fat_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.carbohydrates') AS FLOAT) AS carbohydrates,
    TRY_CAST(json_extract_string(json, '$.nutriments.carbohydrates_100g') AS FLOAT) AS carbohydrates_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.sugars') AS FLOAT) AS sugars,
    TRY_CAST(json_extract_string(json, '$.nutriments.sugars_100g') AS FLOAT) AS sugars_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.fiber') AS FLOAT) AS fiber,
    TRY_CAST(json_extract_string(json, '$.nutriments.fiber_100g') AS FLOAT) AS fiber_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.proteins') AS FLOAT) AS proteins,
    TRY_CAST(json_extract_string(json, '$.nutriments.proteins_100g') AS FLOAT) AS proteins_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.salt') AS FLOAT) AS salt,
    TRY_CAST(json_extract_string(json, '$.nutriments.salt_100g') AS FLOAT) AS salt_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.sodium') AS FLOAT) AS sodium,
    TRY_CAST(json_extract_string(json, '$.nutriments.sodium_100g') AS FLOAT) AS sodium_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.fruits-vegetables-nuts-estimate-from-ingredients_100g') AS FLOAT) AS fruits_vegetables_nuts_estimate_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.fruits-vegetables-nuts_100g') AS FLOAT) AS fruits_vegetables_nuts_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-a') AS FLOAT) AS vitamin_a,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-b1') AS FLOAT) AS vitamin_b1,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-b2') AS FLOAT) AS vitamin_b2,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-pp') AS FLOAT) AS vitamin_pp,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-b6') AS FLOAT) AS vitamin_b6,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-b9') AS FLOAT) AS vitamin_b9,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-b12') AS FLOAT) AS vitamin_b12,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-c') AS FLOAT) AS vitamin_c,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-d') AS FLOAT) AS vitamin_d,
    TRY_CAST(json_extract_string(json, '$.nutriments.vitamin-e') AS FLOAT) AS vitamin_e,
    TRY_CAST(json_extract_string(json, '$.nutriments.pantothenic-acid') AS FLOAT) AS pantothenic_acid,
    TRY_CAST(json_extract_string(json, '$.nova_group') AS INTEGER) AS nova_group,
    TRY_CAST(json_extract_string(json, '$.nutriments.nova-group') AS INTEGER) AS nutriments_nova_group,
    TRY_CAST(json_extract_string(json, '$.nutriments.nova-group_100g') AS INTEGER) AS nova_group_100g,
    TRY_CAST(json_extract_string(json, '$.nutriments.nutrition-score-fr') AS INTEGER) AS nutrition_score_fr,
    TRY_CAST(json_extract_string(json, '$.nutriments.nutrition-score-fr_100g') AS INTEGER) AS nutrition_score_fr_100g,
    json_extract(json, '$.nutrient_levels') AS nutrient_levels
FROM mercadona_ean_products_robust;

-- Add primary key to ean column
ALTER TABLE nutriments_off ADD PRIMARY KEY (ean);

-- Export nutriments_off table to CSV
COPY nutriments_off TO '/home/adrian/code/mercaapi/nutriments_off.csv' (HEADER, DELIMITER ','); 