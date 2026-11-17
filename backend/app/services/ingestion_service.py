"""
KrishiInsights - Ingestion Foundation Service
Supports modular, validated ingestion from canonical CSV datasets into PostgreSQL.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.agriculture import (
    State, District, Crop, AgriculturalRecord, RainfallRecord
)

logger = logging.getLogger("krishiinsights.ingestion")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@dataclass
class IngestionReport:
    dataset_name: str
    total_rows_read: int = 0
    valid_records: int = 0
    skipped_records: int = 0
    inserted_records: int = 0
    errors: List[str] = field(default_factory=list)

    def summary(self) -> Dict:
        return {
            "dataset": self.dataset_name,
            "read": self.total_rows_read,
            "valid": self.valid_records,
            "skipped": self.skipped_records,
            "inserted": self.inserted_records,
            "error_sample": self.errors[:5]
        }

class IngestionManager:
    """
    Manages lookup caches, validation, and staging before database insertion.
    """
    def __init__(self, db: Session):
        self.db = db
        self._state_cache: Dict[str, int] = {}
        self._district_cache: Dict[Tuple[int, str], int] = {}
        self._crop_cache: Dict[str, int] = {}
        self.refresh_caches()

    def refresh_caches(self):
        """Loads reference IDs into memory to avoid repeated queries during batch ingestion."""
        states = self.db.execute(select(State)).scalars().all()
        self._state_cache = {s.state_name.strip().lower(): s.id for s in states}

        districts = self.db.execute(select(District)).scalars().all()
        self._district_cache = {(d.state_id, d.district_name.strip().lower()): d.id for d in districts}

        crops = self.db.execute(select(Crop)).scalars().all()
        self._crop_cache = {c.crop_name.strip().lower(): c.id for c in crops}

    def get_or_create_state(self, state_name: str) -> int:
        clean_name = state_name.strip()
        key = clean_name.lower()
        if key in self._state_cache:
            return self._state_cache[key]
        
        state = State(state_name=clean_name)
        self.db.add(state)
        self.db.flush()
        self._state_cache[key] = state.id
        return state.id

    def get_or_create_district(self, state_id: int, district_name: str) -> int:
        clean_name = district_name.strip()
        key = (state_id, clean_name.lower())
        if key in self._district_cache:
            return self._district_cache[key]
        
        district = District(state_id=state_id, district_name=clean_name)
        self.db.add(district)
        self.db.flush()
        self._district_cache[key] = district.id
        return district.id

    def get_or_create_crop(self, crop_name: str, category: Optional[str] = None) -> int:
        clean_name = crop_name.strip()
        key = clean_name.lower()
        if key in self._crop_cache:
            return self._crop_cache[key]
        
        crop = Crop(crop_name=clean_name, crop_category=category)
        self.db.add(crop)
        self.db.flush()
        self._crop_cache[key] = crop.id
        return crop.id

    def validate_crop_row(self, row: pd.Series) -> Tuple[bool, Optional[str]]:
        """
        Validates individual crop records according to agricultural integrity rules.
        """
        if pd.isna(row.get('Area')) or row['Area'] <= 0:
            return False, "Non-positive or null cultivated area"
        if pd.isna(row.get('Production')) or row['Production'] < 0:
            return False, "Missing or negative production"
        if pd.isna(row.get('State_Name')) or not str(row['State_Name']).strip():
            return False, "Missing state name"
        if pd.isna(row.get('Crop')) or not str(row['Crop']).strip():
            return False, "Missing crop name"
        return True, None

    def dry_run_crop_file(self, file_path: str, max_rows: int = 1000) -> IngestionReport:
        """
        Simulates an ingestion run on a file sample to verify data compliance.
        """
        report = IngestionReport(dataset_name=os.path.basename(file_path))
        df = pd.read_csv(file_path, nrows=max_rows)
        report.total_rows_read = len(df)

        for idx, row in df.iterrows():
            valid, reason = self.validate_crop_row(row)
            if valid:
                report.valid_records += 1
            else:
                report.skipped_records += 1
                if reason and len(report.errors) < 10:
                    report.errors.append(f"Row {idx}: {reason}")

        return report
