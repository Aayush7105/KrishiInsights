"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-17 20:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. States table
    op.create_table(
        'states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('state_name', sa.String(length=100), nullable=False),
        sa.Column('source_code', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('state_name')
    )
    op.create_index(op.f('ix_states_id'), 'states', ['id'], unique=False)
    op.create_index(op.f('ix_states_state_name'), 'states', ['state_name'], unique=True)

    # 2. Districts table
    op.create_table(
        'districts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('state_id', sa.Integer(), nullable=False),
        sa.Column('district_name', sa.String(length=100), nullable=False),
        sa.Column('source_code', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['state_id'], ['states.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('state_id', 'district_name', name='uq_state_district')
    )
    op.create_index(op.f('ix_districts_id'), 'districts', ['id'], unique=False)
    op.create_index(op.f('ix_districts_district_name'), 'districts', ['district_name'], unique=False)
    op.create_index(op.f('ix_districts_state_id'), 'districts', ['state_id'], unique=False)

    # 3. Crops table
    op.create_table(
        'crops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crop_name', sa.String(length=100), nullable=False),
        sa.Column('crop_category', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('crop_name')
    )
    op.create_index(op.f('ix_crops_id'), 'crops', ['id'], unique=False)
    op.create_index(op.f('ix_crops_crop_name'), 'crops', ['crop_name'], unique=True)
    op.create_index(op.f('ix_crops_crop_category'), 'crops', ['crop_category'], unique=False)

    # 4. Agricultural Records table
    op.create_table(
        'agricultural_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('state_id', sa.Integer(), nullable=False),
        sa.Column('district_id', sa.Integer(), nullable=False),
        sa.Column('crop_id', sa.Integer(), nullable=False),
        sa.Column('season', sa.String(length=30), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('area', sa.Float(), nullable=False),
        sa.Column('production', sa.Float(), nullable=False),
        sa.Column('yield_amount', sa.Float(), nullable=False),
        sa.Column('area_unit', sa.String(length=30), nullable=False),
        sa.Column('production_unit', sa.String(length=30), nullable=False),
        sa.Column('yield_unit', sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
        sa.ForeignKeyConstraint(['state_id'], ['states.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('state_id', 'district_id', 'crop_id', 'season', 'year', name='uq_agri_record')
    )
    op.create_index(op.f('ix_agricultural_records_id'), 'agricultural_records', ['id'], unique=False)
    op.create_index(op.f('ix_agricultural_records_state_id'), 'agricultural_records', ['state_id'], unique=False)
    op.create_index(op.f('ix_agricultural_records_district_id'), 'agricultural_records', ['district_id'], unique=False)
    op.create_index(op.f('ix_agricultural_records_crop_id'), 'agricultural_records', ['crop_id'], unique=False)
    op.create_index(op.f('ix_agricultural_records_season'), 'agricultural_records', ['season'], unique=False)
    op.create_index(op.f('ix_agricultural_records_year'), 'agricultural_records', ['year'], unique=False)
    op.create_index(op.f('ix_agricultural_records_yield_amount'), 'agricultural_records', ['yield_amount'], unique=False)

    # 5. Rainfall Records table
    op.create_table(
        'rainfall_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('state_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('annual_rainfall_mm', sa.Float(), nullable=True),
        sa.Column('monsoon_rainfall_mm', sa.Float(), nullable=True),
        sa.Column('rabi_rainfall_mm', sa.Float(), nullable=True),
        sa.Column('pre_monsoon_rainfall_mm', sa.Float(), nullable=True),
        sa.Column('source_id', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['state_id'], ['states.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('state_id', 'year', name='uq_state_year_rainfall')
    )
    op.create_index(op.f('ix_rainfall_records_id'), 'rainfall_records', ['id'], unique=False)
    op.create_index(op.f('ix_rainfall_records_state_id'), 'rainfall_records', ['state_id'], unique=False)
    op.create_index(op.f('ix_rainfall_records_year'), 'rainfall_records', ['year'], unique=False)

    # 6. Prediction Records table
    op.create_table(
        'prediction_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('input_features', sa.JSON(), nullable=False),
        sa.Column('predicted_yield', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=30), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prediction_records_id'), 'prediction_records', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('prediction_records')
    op.drop_table('rainfall_records')
    op.drop_table('agricultural_records')
    op.drop_table('crops')
    op.drop_table('districts')
    op.drop_table('states')
