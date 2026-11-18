"""
KrishiInsights ML Module - Database Connection & Data Access Layer
Queries the primary Neon Serverless PostgreSQL database efficiently.
"""

import os
import sys
import logging
from typing import Optional, Tuple, Dict, Any
import pandas as pd
from dotenv import dotenv_values, load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

# Configure module logger
logger = logging.getLogger("krishiinsights.ml.database")
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# Determine root directory
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.abspath(os.path.join(_current_dir, "..", "..", ".."))

# Load environment configuration
load_dotenv(os.path.join(_root_dir, ".env.local"))
load_dotenv(os.path.join(_root_dir, ".env"))
load_dotenv(os.path.join(_root_dir, "backend", ".env"))

_ENGINE: Optional[Engine] = None
_SESSION_FACTORY: Optional[sessionmaker] = None

def _normalize_url(url: str) -> str:
    """Normalizes PostgreSQL URLs to use psycopg2 dialect for SQLAlchemy."""
    if not url:
        return url
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url

def get_engine() -> Engine:
    """Returns singleton SQLAlchemy Engine connected to primary Neon database."""
    global _ENGINE
    if _ENGINE is None:
        raw_url = os.getenv("DATABASE_URL")
        if not raw_url:
            raise ValueError(
                "CRITICAL: DATABASE_URL environment variable is missing. "
                "Ensure .env or .env.local contains Neon credentials."
            )
        db_url = _normalize_url(raw_url)
        _ENGINE = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    return _ENGINE

def get_session() -> Session:
    """Returns a new SQLAlchemy Session against Neon."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SESSION_FACTORY()

def run_query(sql_query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Executes a SQL query against Neon and returns a Pandas DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql_query), conn, params=params or {})
    return df

def load_agricultural_data(
    crop_name: Optional[str] = None,
    state_name: Optional[str] = None,
    season: Optional[str] = None,
    year_range: Optional[Tuple[int, int]] = None,
    exclude_coconut: bool = False
) -> pd.DataFrame:
    """
    Fetches filtered agricultural records joined with state, district, and crop metadata.
    """
    query = """
        SELECT 
            a.id,
            s.state_name,
            d.district_name,
            c.crop_name,
            c.crop_category,
            a.season,
            a.year,
            a.area,
            a.production,
            a.yield_amount,
            a.area_unit,
            a.production_unit,
            a.yield_unit
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN districts d ON a.district_id = d.id
        JOIN crops c ON a.crop_id = c.id
        WHERE 1=1
    """
    params = {}
    if crop_name:
        query += " AND c.crop_name = :crop_name"
        params["crop_name"] = crop_name
    if state_name:
        query += " AND s.state_name = :state_name"
        params["state_name"] = state_name
    if season:
        query += " AND a.season = :season"
        params["season"] = season
    if year_range:
        query += " AND a.year >= :min_year AND a.year <= :max_year"
        params["min_year"] = year_range[0]
        params["max_year"] = year_range[1]
    if exclude_coconut:
        query += " AND a.yield_unit != 'Nuts/Hectare'"

    query += " ORDER BY a.year, s.state_name, d.district_name, c.crop_name;"
    df = run_query(query, params)
    if not df.empty:
        df["yield"] = df["yield_amount"]
        df["crop_year"] = df["year"]
        df["season_name"] = df["season"]
    return df

def load_rainfall_data(
    state_name: Optional[str] = None,
    year_range: Optional[Tuple[int, int]] = None
) -> pd.DataFrame:
    """
    Fetches historical rainfall records joined with state metadata.
    """
    query = """
        SELECT 
            r.id,
            s.state_name,
            r.year,
            r.annual_rainfall_mm,
            r.monsoon_rainfall_mm,
            r.rabi_rainfall_mm,
            r.pre_monsoon_rainfall_mm,
            r.source_id
        FROM rainfall_records r
        JOIN states s ON r.state_id = s.id
        WHERE 1=1
    """
    params = {}
    if state_name:
        query += " AND s.state_name = :state_name"
        params["state_name"] = state_name
    if year_range:
        query += " AND r.year >= :min_year AND r.year <= :max_year"
        params["min_year"] = year_range[0]
        params["max_year"] = year_range[1]

    query += " ORDER BY r.year, s.state_name;"
    return run_query(query, params)

def load_aligned_agri_rainfall_data(
    crop_name: Optional[str] = None,
    state_name: Optional[str] = None,
    exclude_coconut: bool = True
) -> pd.DataFrame:
    """
    Loads seasonally aligned agricultural records and rainfall metrics
    for the overlapping 1997-2015 historical period.
    """
    query = """
        SELECT 
            a.year,
            s.state_name,
            d.district_name,
            c.crop_name,
            c.crop_category,
            a.season,
            a.area,
            a.production,
            a.yield_amount,
            a.yield_unit,
            r.annual_rainfall_mm,
            r.monsoon_rainfall_mm,
            r.rabi_rainfall_mm,
            r.pre_monsoon_rainfall_mm
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN districts d ON a.district_id = d.id
        JOIN crops c ON a.crop_id = c.id
        JOIN rainfall_records r ON a.state_id = r.state_id AND a.year = r.year
        WHERE a.year >= 1997 AND a.year <= 2015
    """
    params = {}
    if crop_name:
        query += " AND c.crop_name = :crop_name"
        params["crop_name"] = crop_name
    if state_name:
        query += " AND s.state_name = :state_name"
        params["state_name"] = state_name
    if exclude_coconut:
        query += " AND a.yield_unit != 'Nuts/Hectare'"

    query += " ORDER BY a.year, s.state_name, c.crop_name;"
    return run_query(query, params)
