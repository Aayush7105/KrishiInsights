"""
KrishiInsights - Data Ingestion Service
Supports robust, idempotent batch ingestion into PostgreSQL (krishiinsights_db).
"""

import os
import sys
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.agriculture import (
    State, District, Crop, AgriculturalRecord, RainfallRecord
)

logger = logging.getLogger("krishiinsights.ingestion")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Mapping of all 124 crops to standard ICAR / DES classification categories
CROP_CATEGORY_MAP = {
    # Cereals & Millets
    'Rice': 'Cereal', 'Paddy': 'Cereal', 'Wheat': 'Cereal', 'Maize': 'Coarse Cereal',
    'Bajra': 'Coarse Cereal', 'Jowar': 'Coarse Cereal', 'Barley': 'Cereal', 'Ragi': 'Coarse Cereal',
    'Small millets': 'Coarse Cereal', 'Samai': 'Coarse Cereal', 'Varagu': 'Coarse Cereal',
    'Korra': 'Coarse Cereal', 'Jobster': 'Coarse Cereal', 'Other Cereals & Millets': 'Coarse Cereal',
    'Total foodgrain': 'Total Foodgrain',
    # Pulses
    'Arhar/Tur': 'Pulse', 'Gram': 'Pulse', 'Urad': 'Pulse', 'Moong(Green Gram)': 'Pulse',
    'Masoor': 'Pulse', 'Blackgram': 'Pulse', 'Horse-gram': 'Pulse', 'Lentil': 'Pulse',
    'Moth': 'Pulse', 'Khesari': 'Pulse', 'Cowpea(Lobia)': 'Pulse', 'Rajmash Kholar': 'Pulse',
    'Ricebean (nagadal)': 'Pulse', 'Peas & beans (Pulses)': 'Pulse', 'Other Kharif pulses': 'Pulse',
    'Other  Rabi pulses': 'Pulse', 'other misc. pulses': 'Pulse', 'Pulses total': 'Pulse Total',
    # Oilseeds
    'Groundnut': 'Oilseed', 'Rapeseed &Mustard': 'Oilseed', 'Soyabean': 'Oilseed',
    'Sunflower': 'Oilseed', 'Sesamum': 'Oilseed', 'Castor seed': 'Oilseed', 'Linseed': 'Oilseed',
    'Safflower': 'Oilseed', 'Niger seed': 'Oilseed', 'other oilseeds': 'Oilseed', 'Oilseeds total': 'Oilseed Total',
    # Fiber
    'Cotton(lint)': 'Fiber', 'Kapas': 'Fiber', 'Jute': 'Fiber', 'Mesta': 'Fiber',
    'Jute & mesta': 'Fiber', 'Sannhamp': 'Fiber', 'other fibres': 'Fiber',
    # Commercial & Plantation
    'Sugarcane': 'Commercial', 'Tobacco': 'Commercial', 'Tea': 'Plantation',
    'Coffee': 'Plantation', 'Rubber': 'Plantation', 'Coconut': 'Plantation',
    'Cashewnut': 'Plantation', 'Cashewnut Processed': 'Plantation', 'Cashewnut Raw': 'Plantation',
    'Perilla': 'Commercial', 'Guar seed': 'Commercial',
    # Spices
    'Arecanut': 'Spices', 'Arcanut (Processed)': 'Spices', 'Atcanut (Raw)': 'Spices',
    'Black pepper': 'Spices', 'Cardamom': 'Spices', 'Coriander': 'Spices',
    'Dry chillies': 'Spices', 'Dry ginger': 'Spices', 'Garlic': 'Spices',
    'Ginger': 'Spices', 'Turmeric': 'Spices', 'Cond-spcs other': 'Spices',
    # Fruits
    'Apple': 'Fruit', 'Banana': 'Fruit', 'Citrus Fruit': 'Fruit', 'Grapes': 'Fruit',
    'Mango': 'Fruit', 'Orange': 'Fruit', 'Papaya': 'Fruit', 'Pineapple': 'Fruit',
    'Sapota': 'Fruit', 'Jack Fruit': 'Fruit', 'Lemon': 'Fruit', 'Litchi': 'Fruit',
    'Peach': 'Fruit', 'Pear': 'Fruit', 'Plums': 'Fruit', 'Pome Fruit': 'Fruit',
    'Pome Granet': 'Fruit', 'Water Melon': 'Fruit', 'Ber': 'Fruit',
    'Other Citrus Fruit': 'Fruit', 'Other Dry Fruit': 'Fruit', 'Other Fresh Fruits': 'Fruit',
    # Vegetables
    'Onion': 'Vegetable', 'Potato': 'Vegetable', 'Tomato': 'Vegetable', 'Brinjal': 'Vegetable',
    'Cabbage': 'Vegetable', 'Cauliflower': 'Vegetable', 'Bhindi': 'Vegetable', 'Bitter Gourd': 'Vegetable',
    'Bottle Gourd': 'Vegetable', 'Ash Gourd': 'Vegetable', 'Carrot': 'Vegetable', 'Beet Root': 'Vegetable',
    'Bean': 'Vegetable', 'Beans & Mutter(Vegetable)': 'Vegetable', 'Cucumber': 'Vegetable',
    'Drum Stick': 'Vegetable', 'Colocosia': 'Vegetable', 'Peas  (vegetable)': 'Vegetable',
    'Pump Kin': 'Vegetable', 'Redish': 'Vegetable', 'Ribed Guard': 'Vegetable', 'Snak Guard': 'Vegetable',
    'Sweet potato': 'Vegetable', 'Tapioca': 'Vegetable', 'Turnip': 'Vegetable', 'Yam': 'Vegetable',
    'Lab-Lab': 'Vegetable', 'Other Vegetables': 'Vegetable'
}

# IMD 36 Subdivisions to Indian States mapping
SUBDIVISION_TO_STATES = {
    'ANDAMAN & NICOBAR ISLANDS': ['Andaman and Nicobar Islands'],
    'ARUNACHAL PRADESH': ['Arunachal Pradesh'],
    'ASSAM & MEGHALAYA': ['Assam', 'Meghalaya'],
    'BIHAR': ['Bihar'],
    'CHHATTISGARH': ['Chhattisgarh'],
    'COASTAL ANDHRA PRADESH': ['Andhra Pradesh'],
    'RAYALSEEMA': ['Andhra Pradesh'],
    'COASTAL KARNATAKA': ['Karnataka'],
    'NORTH INTERIOR KARNATAKA': ['Karnataka'],
    'SOUTH INTERIOR KARNATAKA': ['Karnataka'],
    'EAST MADHYA PRADESH': ['Madhya Pradesh'],
    'WEST MADHYA PRADESH': ['Madhya Pradesh'],
    'EAST RAJASTHAN': ['Rajasthan'],
    'WEST RAJASTHAN': ['Rajasthan'],
    'EAST UTTAR PRADESH': ['Uttar Pradesh'],
    'WEST UTTAR PRADESH': ['Uttar Pradesh'],
    'GANGETIC WEST BENGAL': ['West Bengal'],
    'SUB HIMALAYAN WEST BENGAL & SIKKIM': ['West Bengal', 'Sikkim'],
    'GUJARAT REGION': ['Gujarat'],
    'SAURASHTRA & KUTCH': ['Gujarat', 'Dadra and Nagar Haveli'],
    'HARYANA DELHI & CHANDIGARH': ['Haryana', 'Chandigarh'],
    'HIMACHAL PRADESH': ['Himachal Pradesh'],
    'JAMMU & KASHMIR': ['Jammu and Kashmir'],
    'JHARKHAND': ['Jharkhand'],
    'KERALA': ['Kerala'],
    'KONKAN & GOA': ['Goa', 'Maharashtra'],
    'MADHYA MAHARASHTRA': ['Maharashtra'],
    'MATATHWADA': ['Maharashtra'],
    'VIDARBHA': ['Maharashtra'],
    'NAGA MANI MIZO TRIPURA': ['Nagaland', 'Manipur', 'Mizoram', 'Tripura'],
    'ORISSA': ['Odisha'],
    'PUNJAB': ['Punjab'],
    'TAMIL NADU': ['Tamil Nadu', 'Puducherry'],
    'TELANGANA': ['Telangana'],
    'UTTARAKHAND': ['Uttarakhand']
}

@dataclass
class IngestionStats:
    states_inserted: int = 0
    districts_inserted: int = 0
    crops_inserted: int = 0
    rainfall_inserted: int = 0
    agri_records_inserted: int = 0
    agri_records_skipped: int = 0
    start_time: float = field(default_factory=time.time)
    elapsed_seconds: float = 0.0

class IngestionPipeline:
    def __init__(self, session: Session):
        self.session = session
        self.stats = IngestionStats()
        self.state_cache: Dict[str, int] = {}
        self.district_cache: Dict[Tuple[int, str], int] = {}
        self.crop_cache: Dict[str, int] = {}

    def load_cache(self):
        """Loads state, district, and crop IDs into memory for rapid foreign key resolution."""
        states = self.session.execute(select(State.id, State.state_name)).all()
        self.state_cache = {s[1].strip().lower(): s[0] for s in states}

        districts = self.session.execute(select(District.id, District.state_id, District.district_name)).all()
        self.district_cache = {(d[1], d[2].strip().lower()): d[0] for d in districts}

        crops = self.session.execute(select(Crop.id, Crop.crop_name)).all()
        self.crop_cache = {c[1].strip().lower(): c[0] for c in crops}
        logger.info(f"Loaded cache: {len(self.state_cache)} states, {len(self.district_cache)} districts, {len(self.crop_cache)} crops.")

    def populate_lookup_tables(self, crop_csv_path: str):
        """
        Populates states, districts, and crops lookup tables idempotently.
        """
        logger.info("--- Step 1: Populating Lookup Tables ---")
        df = pd.read_csv(crop_csv_path)

        # 1. States
        unique_states = sorted(df['State'].dropna().astype(str).str.strip().unique())
        for state_name in unique_states:
            stmt = pg_insert(State).values(state_name=state_name).on_conflict_do_nothing(index_elements=['state_name'])
            self.session.execute(stmt)
        self.session.commit()

        # Reload state cache
        states = self.session.execute(select(State.id, State.state_name)).all()
        self.state_cache = {s[1].strip().lower(): s[0] for s in states}
        self.stats.states_inserted = len(self.state_cache)
        logger.info(f"States verified: {len(self.state_cache)} states.")

        # 2. Districts (state_id + district_name)
        dist_df = df[['State', 'District']].drop_duplicates()
        for _, row in dist_df.iterrows():
            st_name = str(row['State']).strip().lower()
            d_name = str(row['District']).strip()
            state_id = self.state_cache.get(st_name)
            if state_id and d_name:
                stmt = pg_insert(District).values(
                    state_id=state_id, district_name=d_name
                ).on_conflict_do_nothing(constraint='uq_state_district')
                self.session.execute(stmt)
        self.session.commit()

        # Reload district cache
        districts = self.session.execute(select(District.id, District.state_id, District.district_name)).all()
        self.district_cache = {(d[1], d[2].strip().lower()): d[0] for d in districts}
        self.stats.districts_inserted = len(self.district_cache)
        logger.info(f"Districts verified: {len(self.district_cache)} districts.")

        # 3. Crops
        unique_crops = sorted(df['Crop'].dropna().astype(str).str.strip().unique())
        for crop_name in unique_crops:
            category = CROP_CATEGORY_MAP.get(crop_name, "Other")
            stmt = pg_insert(Crop).values(
                crop_name=crop_name, crop_category=category
            ).on_conflict_do_nothing(index_elements=['crop_name'])
            self.session.execute(stmt)
        self.session.commit()

        # Reload crop cache
        crops = self.session.execute(select(Crop.id, Crop.crop_name)).all()
        self.crop_cache = {c[1].strip().lower(): c[0] for c in crops}
        self.stats.crops_inserted = len(self.crop_cache)
        logger.info(f"Crops verified: {len(self.crop_cache)} crops with category mappings.")

    def ingest_rainfall(self, raw_rain_path: str):
        """
        Preprocesses and ingests historical meteorological rainfall records into PostgreSQL.
        """
        logger.info("--- Step 2: Ingesting Rainfall Records ---")
        df = pd.read_csv(raw_rain_path)
        df['SUBDIVISION'] = df['SUBDIVISION'].astype(str).str.strip()

        # Handle missing monthly / seasonal values by subdivision median
        monthly_cols = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        seasonal_cols = ['ANNUAL', 'Jan-Feb', 'Mar-May', 'Jun-Sep', 'Oct-Dec']
        for col in monthly_cols + seasonal_cols:
            df[col] = df.groupby('SUBDIVISION')[col].transform(lambda g: g.fillna(g.median()))
            df[col] = df[col].fillna(df[col].median())

        # Map Subdivisions to Indian States
        records = []
        for _, row in df.iterrows():
            sub = row['SUBDIVISION']
            if sub in SUBDIVISION_TO_STATES:
                for state in SUBDIVISION_TO_STATES[sub]:
                    rec = row.to_dict()
                    rec['State'] = state
                    records.append(rec)

        mapped_df = pd.DataFrame(records)
        state_rain = mapped_df.groupby(['State', 'YEAR'], as_index=False).agg({
            'ANNUAL': 'mean',
            'Jun-Sep': 'mean',
            'Oct-Dec': 'mean',
            'Jan-Feb': 'mean',
            'Mar-May': 'mean'
        })

        rainfall_entries = []
        for _, row in state_rain.iterrows():
            st_key = str(row['State']).strip().lower()
            state_id = self.state_cache.get(st_key)
            if not state_id:
                continue

            rabi = round(float(row['Oct-Dec']) + float(row['Jan-Feb']), 2)
            rainfall_entries.append({
                "state_id": state_id,
                "year": int(row['YEAR']),
                "annual_rainfall_mm": round(float(row['ANNUAL']), 2),
                "monsoon_rainfall_mm": round(float(row['Jun-Sep']), 2),
                "rabi_rainfall_mm": rabi,
                "pre_monsoon_rainfall_mm": round(float(row['Mar-May']), 2),
                "source_id": "IMD"
            })

        # Batch insert with idempotent on_conflict_do_nothing
        batch_size = 1000
        for i in range(0, len(rainfall_entries), batch_size):
            batch = rainfall_entries[i:i + batch_size]
            stmt = pg_insert(RainfallRecord).values(batch).on_conflict_do_nothing(
                constraint='uq_state_year_rainfall'
            )
            self.session.execute(stmt)

        self.session.commit()
        cnt = self.session.execute(select(func.count(RainfallRecord.id))).scalar()
        self.stats.rainfall_inserted = cnt
        logger.info(f"Rainfall ingestion complete: {cnt:,} total records verified in database.")

    def ingest_agricultural_records(self, clean_crop_csv_path: str, batch_size: int = 5000, max_rows: Optional[int] = None):
        """
        Batch ingests validated agricultural records into PostgreSQL with foreign-key resolution.
        """
        logger.info(f"--- Step 3: Ingesting Agricultural Records (Batch size: {batch_size:,}) ---")
        df = pd.read_csv(clean_crop_csv_path)
        if max_rows:
            df = df.iloc[:max_rows]
            logger.info(f"Running limited test ingestion on {max_rows:,} records.")

        total_rows = len(df)
        records_to_insert = []
        skipped = 0
        processed_count = 0

        t0 = time.time()
        for idx, row in df.iterrows():
            st_key = str(row['State']).strip().lower()
            dist_key = str(row['District']).strip().lower()
            crop_key = str(row['Crop']).strip().lower()

            state_id = self.state_cache.get(st_key)
            crop_id = self.crop_cache.get(crop_key)

            if not state_id or not crop_id:
                skipped += 1
                continue

            district_id = self.district_cache.get((state_id, dist_key))
            if not district_id:
                skipped += 1
                continue

            area = float(row['Area'])
            prod = float(row['Production'])
            yd = float(row['Yield'])

            records_to_insert.append({
                "state_id": state_id,
                "district_id": district_id,
                "crop_id": crop_id,
                "season": str(row['Season']).strip(),
                "year": int(row['Year']),
                "area": area,
                "production": prod,
                "yield_amount": yd,
                "area_unit": str(row.get('Area_Unit', 'Hectares')),
                "production_unit": str(row.get('Production_Unit', 'Tonnes')),
                "yield_unit": str(row.get('Yield_Unit', 'Tonnes/Hectare'))
            })

            # Batch execution
            if len(records_to_insert) >= batch_size:
                stmt = pg_insert(AgriculturalRecord).values(records_to_insert).on_conflict_do_nothing(
                    constraint='uq_agri_record'
                )
                self.session.execute(stmt)
                self.session.commit()
                processed_count += len(records_to_insert)
                logger.info(f"Progress: {processed_count:,} / {total_rows:,} records processed ({time.time() - t0:.1f}s)...")
                records_to_insert = []

        # Insert remaining records in final batch
        if records_to_insert:
            stmt = pg_insert(AgriculturalRecord).values(records_to_insert).on_conflict_do_nothing(
                constraint='uq_agri_record'
            )
            self.session.execute(stmt)
            self.session.commit()
            processed_count += len(records_to_insert)

        actual_count = self.session.execute(select(func.count(AgriculturalRecord.id))).scalar()
        self.stats.agri_records_inserted = actual_count
        self.stats.agri_records_skipped = skipped
        self.stats.elapsed_seconds = round(time.time() - self.stats.start_time, 2)
        logger.info(f"Agricultural records ingestion complete: {actual_count:,} total records in database, {skipped} skipped in {self.stats.elapsed_seconds}s.")

    def run_full_pipeline(self, crop_path: str, rain_path: str):
        """Executes the complete three-step ingestion pipeline."""
        self.populate_lookup_tables(crop_path)
        self.ingest_rainfall(rain_path)
        self.ingest_agricultural_records(crop_path)
        return self.stats
