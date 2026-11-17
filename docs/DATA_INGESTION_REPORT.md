# KrishiInsights — Stage 3 Data Ingestion & Database Verification Report

> **Project:** KrishiInsights — Agricultural Data Analytics and Crop Yield Intelligence Platform  
> **Stage:** Stage 3 — Data Cleaning, Preprocessing, Validation & PostgreSQL Full Ingestion  
> **Database:** PostgreSQL 17 (`krishiinsights_db` on `localhost:5432`)  
> **Execution Date:** November 17, 2026  
> **Status:** Completed & 100% Verified

---

## 1. Executive Summary

Stage 3 successfully executed the complete data cleaning, validation, and batch ingestion pipeline for the historical Indian agricultural and meteorological datasets into PostgreSQL 17.

All lookup entities (`states`, `districts`, `crops`) were populated idempotently with standard agricultural classifications. The full **242,296 validated agricultural records** and **3,772 historical meteorological rainfall records** have been ingested with zero foreign key violations, zero orphan records, and strict yield unit isolation.

---

## 2. PostgreSQL Table Record Counts

| Table Name | Entity Description | Record Count | Integrity Status |
| :--- | :--- | :--- | :--- |
| `states` | Indian States and Union Territories | **33** | Verified unique |
| `districts` | Administrative districts scoped by state | **652** | Unique per `(state_id, district_name)` |
| `crops` | Standardized crops with ICAR/DES categories | **124** | Standardized categories assigned |
| `agricultural_records` | Cleaned crop production & yield records (1997–2015) | **242,296** | 0 orphans, 0 null yields, 0 invalid areas |
| `rainfall_records` | IMD state-aligned rainfall records (1901–2015) | **3,772** | 0 orphans, all months complete |
| `prediction_records` | ML inference audit log | **0** | Ready for Stage 10 |

---

## 3. Data Cleaning & Validation Audit

### 3.1 Raw Dataset Quality Breakdown
* **Raw Agricultural Observations:** 246,091 records (`datasets/raw/crop_production.csv`).
* **Missing Production Values:** 3,730 records (1.52%) contained null or unrecorded production values.
  * *Action:* In accordance with Section 4 of `AGENTS.md`, missing production cannot be imputed or replaced with zero because that would artificially skew yield statistics. These records were filtered out during preprocessing.
* **Non-Positive Area:** Records with $\text{Area} \le 0$ were filtered out to avoid division-by-zero errors.
* **Extreme Outlier Filtering:** 65 records with catastrophic reporting errors (e.g., maize yields $>2,000\text{ t/ha}$) were removed during cleaning.
* **Final Cleaned Ingestion Count:** **242,296 records** (`datasets/processed/clean_crop_data.csv`).

### 3.2 Strict Yield Calculation Formula
In accordance with Rule 4.5 of `AGENTS.md`:
$$\text{Yield} = \frac{\text{Production}}{\text{Cultivated Area}}$$
* Yield is calculated **only** when both production and cultivated area have positive values ($\text{Area} > 0$).
* No null yield records exist in the database (`COUNT(*) FILTER (WHERE yield_amount IS NULL) = 0`).

---

## 4. Measurement Unit Integrity & Isolation

Agricultural reporting in India uses two distinct measurement systems that must never be mathematically mixed:

| Crop Category | Example Crops | Production Unit | Yield Unit | Database Record Count |
| :--- | :--- | :--- | :--- | :--- |
| **Field & Horticultural Crops** | Rice, Wheat, Maize, Cotton, Pulses, Sugarcane | **Tonnes** | **Tonnes/Hectare** | **240,338** |
| **Plantation Tree Crops** | Coconut | **Number of Nuts** | **Nuts/Hectare** | **1,958** |
| **Total Ingested** | | | | **242,296** |

Every row in `agricultural_records` explicitly stores its `production_unit` and `yield_unit` to ensure that analytical aggregations (e.g., average yield) never average nuts with metric tonnes.

---

## 5. Crop Category Standardization

All 124 distinct crops were mapped into standard agricultural groups based on Indian Council of Agricultural Research (ICAR) and DES taxonomy:

1. **Cereal & Coarse Cereal:** Rice (15,081 records), Maize (13,781 records), Wheat (7,878 records), Bajra (5,388 records), Jowar (6,990 records), Barley, Ragi, Small millets.
2. **Pulses:** Moong (10,106 records), Urad (9,710 records), Gram (7,335 records), Arhar/Tur (7,572 records), Masoor, Horse-gram.
3. **Oilseeds:** Sesamum (8,820 records), Groundnut (8,770 records), Rapeseed & Mustard (7,533 records), Sunflower, Soyabean, Linseed.
4. **Fibers:** Cotton(lint) (4,751 records), Jute, Mesta, Sannhamp.
5. **Commercial & Plantation:** Sugarcane (7,828 records), Coconut (1,958 records), Tobacco, Tea, Coffee, Rubber, Cashewnut.
6. **Spices:** Dry chillies (6,467 records), Coriander (3,311 records), Garlic, Turmeric, Ginger, Black pepper.
7. **Vegetables & Fruits:** Potato (6,907 records), Onion (6,984 records), Banana (3,264 records), Sweet potato, Tapioca, Tomato.

---

## 6. Referential Integrity & Idempotency Audit

### 6.1 Foreign Key Referential Integrity Checks
* **Orphan Agricultural $\to$ State:** 0
* **Orphan Agricultural $\to$ District:** 0
* **Orphan Agricultural $\to$ Crop:** 0
* **Orphan District $\to$ State:** 0
* **Orphan Rainfall $\to$ State:** 0
* **Integrity Status:** **100% CLEAN** — All foreign key relationships resolved successfully.

### 6.2 Spatial Granularity Resolution (Districts)
* There are 646 distinct district names across India, but **652 unique state-district pairs**.
* Duplicate names across different states (e.g., "AURANGABAD" in Bihar and Maharashtra; "BILASPUR" in Himachal Pradesh and Chhattisgarh; "HAMIRPUR" in HP and UP; "PRATAPGARH" in Rajasthan and UP) are cleanly separated by the composite unique constraint `uq_state_district (state_id, district_name)`.

### 6.3 Idempotency Verification
* When `scripts/run_ingestion.py` was re-executed over already-ingested records, the PostgreSQL `ON CONFLICT DO NOTHING` clauses ensured that **0 duplicate records** were created.

---

## 7. Verification Queries for pgAdmin 4 / psql

Developers and examiners can run the following SQL queries in pgAdmin 4 or `psql` to verify database health:

```sql
-- 1. Verify table counts
SELECT 'states' AS entity, COUNT(*) AS count FROM states
UNION ALL
SELECT 'districts', COUNT(*) FROM districts
UNION ALL
SELECT 'crops', COUNT(*) FROM crops
UNION ALL
SELECT 'rainfall_records', COUNT(*) FROM rainfall_records
UNION ALL
SELECT 'agricultural_records', COUNT(*) FROM agricultural_records;

-- 2. Verify yield unit distribution
SELECT yield_unit, production_unit, COUNT(*) AS total_records
FROM agricultural_records
GROUP BY yield_unit, production_unit;

-- 3. Verify zero orphan records
SELECT 
    COUNT(*) FILTER (WHERE s.id IS NULL) AS orphan_states,
    COUNT(*) FILTER (WHERE d.id IS NULL) AS orphan_districts,
    COUNT(*) FILTER (WHERE c.id IS NULL) AS orphan_crops
FROM agricultural_records a
LEFT JOIN states s ON a.state_id = s.id
LEFT JOIN districts d ON a.district_id = d.id
LEFT JOIN crops c ON a.crop_id = c.id;

-- 4. Sample joined agricultural record
SELECT s.state_name, d.district_name, c.crop_name, c.crop_category, 
       a.season, a.year, a.area, a.production, a.yield_amount, a.yield_unit
FROM agricultural_records a
JOIN states s ON a.state_id = s.id
JOIN districts d ON a.district_id = d.id
JOIN crops c ON a.crop_id = c.id
WHERE c.crop_name = 'Rice' AND a.year = 2014
ORDER BY a.yield_amount DESC
LIMIT 5;
```

---

## 8. Automated Test Suite Results

Automated regression tests were implemented in `backend/tests/test_stage3_ingestion.py` and executed via pytest:

```text
============================= test session starts =============================
platform win32 -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0
rootdir: D:\Major Project
plugins: anyio-4.16.0
collected 6 items

backend\tests\test_health.py ..                                          [ 33%]
backend\tests\test_stage3_ingestion.py ....                              [100%]

============================== 6 passed in 2.53s ==============================
```

All unit and database integration tests passed with 100% success.
