from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, JSON, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from app.database.base import Base

class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(String(100), unique=True, nullable=False, index=True)
    source_code = Column(String(50), nullable=True)

    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")
    agricultural_records = relationship("AgriculturalRecord", back_populates="state")
    rainfall_records = relationship("RainfallRecord", back_populates="state")

    def __repr__(self):
        return f"<State(id={self.id}, name='{self.state_name}')>"


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id", ondelete="CASCADE"), nullable=False, index=True)
    district_name = Column(String(100), nullable=False, index=True)
    source_code = Column(String(50), nullable=True)

    state = relationship("State", back_populates="districts")
    agricultural_records = relationship("AgriculturalRecord", back_populates="district")

    __table_args__ = (
        UniqueConstraint("state_id", "district_name", name="uq_state_district"),
    )

    def __repr__(self):
        return f"<District(id={self.id}, name='{self.district_name}', state_id={self.state_id})>"


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), unique=True, nullable=False, index=True)
    crop_category = Column(String(50), nullable=True, index=True)

    agricultural_records = relationship("AgriculturalRecord", back_populates="crop")

    def __repr__(self):
        return f"<Crop(id={self.id}, name='{self.crop_name}')>"


class AgriculturalRecord(Base):
    __tablename__ = "agricultural_records"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, index=True)
    season = Column(String(30), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    area = Column(Float, nullable=False)
    production = Column(Float, nullable=False)
    yield_amount = Column(Float, nullable=False, index=True)
    area_unit = Column(String(30), nullable=False, default="Hectares")
    production_unit = Column(String(30), nullable=False, default="Tonnes")
    yield_unit = Column(String(30), nullable=False, default="Tonnes/Hectare")

    state = relationship("State", back_populates="agricultural_records")
    district = relationship("District", back_populates="agricultural_records")
    crop = relationship("Crop", back_populates="agricultural_records")

    __table_args__ = (
        UniqueConstraint("state_id", "district_id", "crop_id", "season", "year", name="uq_agri_record"),
    )


class RainfallRecord(Base):
    __tablename__ = "rainfall_records"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    annual_rainfall_mm = Column(Float, nullable=True)
    monsoon_rainfall_mm = Column(Float, nullable=True)
    rabi_rainfall_mm = Column(Float, nullable=True)
    pre_monsoon_rainfall_mm = Column(Float, nullable=True)
    source_id = Column(String(50), nullable=False, default="IMD")

    state = relationship("State", back_populates="rainfall_records")

    __table_args__ = (
        UniqueConstraint("state_id", "year", name="uq_state_year_rainfall"),
    )


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)
    input_features = Column(JSON, nullable=False)
    predicted_yield = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False, default="Tonnes/Hectare")
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
