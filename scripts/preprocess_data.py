"""
KrishiInsights - Data Preprocessing & Integration Pipeline
Compliant with KrishiInsights Development Guide (Sections 4 & 5).

Data Sources:
1. Open Government Data Platform (data.gov.in) / Ministry of Agriculture & Farmers Welfare
   - Crop Production Statistics (1997-2015)
2. India Meteorological Department (IMD / mausam.imd.gov.in)
   - Subdivision-wise Historical Rainfall Records (1901-2015)
3. National Data & Analytics Platform (NDAP, NITI Aayog)
   - Indicator consistency & boundary validation
"""

import os
import sys
import numpy as np
import pandas as pd

RAW_CROP_PATH = os.path.join("datasets", "raw", "crop_production.csv")
RAW_RAIN_PATH = os.path.join("datasets", "raw", "rainfall.csv")
PROCESSED_DIR = os.path.join("datasets", "processed")
CLEAN_CROP_PATH = os.path.join(PROCESSED_DIR, "clean_crop_data.csv")
COMBINED_PATH = os.path.join(PROCESSED_DIR, "combined_data.csv")

# Mapping of IMD 36 Meteorological Subdivisions to Indian States & Union Territories
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

def clean_crop_data(raw_crop_path):
    print("--- 1. Loading and Inspecting Raw Crop Data ---")
    df = pd.read_csv(raw_crop_path)
    initial_rows = len(df)
    print(f"Initial raw crop records: {initial_rows:,}")

    # Standardize column names
    col_map = {
        'State_Name': 'State',
        'District_Name': 'District',
        'Crop_Year': 'Year',
        'Season': 'Season',
        'Crop': 'Crop',
        'Area': 'Area',
        'Production': 'Production'
    }
    df = df.rename(columns=col_map)

    # Standardize string fields: strip whitespace, title casing
    for col in ['State', 'District', 'Season', 'Crop']:
        df[col] = df[col].astype(str).str.strip()

    # Normalize state names if any discrepancies exist
    state_aliases = {
        'Orissa': 'Odisha',
        'Andaman and Nicobar Islands': 'Andaman and Nicobar Islands'
    }
    df['State'] = df['State'].replace(state_aliases)

    # Clean Season names
    season_map = {
        'Kharif': 'Kharif',
        'Rabi': 'Rabi',
        'Summer': 'Summer',
        'Autumn': 'Autumn',
        'Winter': 'Winter',
        'Whole Year': 'Whole Year'
    }
    df['Season'] = df['Season'].map(lambda s: season_map.get(s, s))

    # Identify duplicates
    duplicates = df.duplicated(subset=['State', 'District', 'Year', 'Season', 'Crop']).sum()
    print(f"Identified duplicate records: {duplicates}")
    if duplicates > 0:
        df = df.drop_duplicates(subset=['State', 'District', 'Year', 'Season', 'Crop'], keep='first')

    # Missing value handling
    missing_prod = df['Production'].isna().sum()
    print(f"Records with missing Production: {missing_prod:,} ({(missing_prod/initial_rows)*100:.2f}%)")
    
    # Exclude records with missing or non-positive area & missing production
    valid_mask = df['Production'].notna() & df['Area'].notna() & (df['Area'] > 0) & (df['Production'] >= 0)
    df_clean = df[valid_mask].copy()
    print(f"Records retained after filtering non-positive area and missing production: {len(df_clean):,}")

    # Document unit distinctions: Coconut is measured in nuts, others in Tonnes
    is_coconut = df_clean['Crop'].str.contains('Coconut', case=False, na=False)
    df_clean['Area_Unit'] = 'Hectares'
    df_clean['Production_Unit'] = np.where(is_coconut, 'Number of Nuts', 'Tonnes')
    df_clean['Yield_Unit'] = np.where(is_coconut, 'Nuts/Hectare', 'Tonnes/Hectare')

    # Calculate Yield = Production / Area
    df_clean['Yield'] = df_clean['Production'] / df_clean['Area']

    # Quality check / Outlier handling:
    # For non-coconut crops, yields over 200 tonnes/hectare are extreme measurement/reporting anomalies
    # (even high-yield sugarcane rarely exceeds 120-150 t/ha).
    non_coco_anomalies = (~is_coconut) & (df_clean['Yield'] > 200)
    anomaly_count = non_coco_anomalies.sum()
    print(f"Outlier non-coconut records with Yield > 200 Tonnes/Ha removed: {anomaly_count}")
    df_clean = df_clean[~non_coco_anomalies].copy()

    # Round yield and area for clarity
    df_clean['Yield'] = df_clean['Yield'].round(4)
    df_clean['Area'] = df_clean['Area'].round(2)
    df_clean['Production'] = df_clean['Production'].round(2)

    return df_clean

def clean_rainfall_data(raw_rain_path):
    print("\n--- 2. Loading and Preprocessing Rainfall Data ---")
    df = pd.read_csv(raw_rain_path)
    print(f"Initial raw rainfall records: {len(df):,}")

    # Clean string columns
    df['SUBDIVISION'] = df['SUBDIVISION'].astype(str).str.strip()

    # Handle missing monthly / seasonal values by subdivision median
    monthly_cols = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    seasonal_cols = ['ANNUAL', 'Jan-Feb', 'Mar-May', 'Jun-Sep', 'Oct-Dec']
    all_num_cols = monthly_cols + seasonal_cols

    for col in all_num_cols:
        df[col] = df.groupby('SUBDIVISION')[col].transform(lambda grp: grp.fillna(grp.median()))
        # If still NaN, fill with national median
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
    print(f"Subdivision records mapped to states: {len(mapped_df):,} rows")

    # Aggregate by State and Year (handling states spanning multiple subdivisions like Maharashtra, UP, etc.)
    state_rain = mapped_df.groupby(['State', 'YEAR'], as_index=False).agg({
        'ANNUAL': 'mean',
        'Jun-Sep': 'mean', # Monsoon (Kharif)
        'Oct-Dec': 'mean', # Post-monsoon (Rabi early)
        'Jan-Feb': 'mean', # Winter (Rabi late)
        'Mar-May': 'mean'  # Pre-monsoon (Summer)
    })

    # Rename columns to standard, documented schema
    state_rain = state_rain.rename(columns={
        'YEAR': 'Year',
        'ANNUAL': 'Annual_Rainfall_mm',
        'Jun-Sep': 'Monsoon_Rainfall_mm',
        'Oct-Dec': 'Post_Monsoon_Rainfall_mm',
        'Jan-Feb': 'Winter_Rainfall_mm',
        'Mar-May': 'Pre_Monsoon_Rainfall_mm'
    })

    # Calculate combined Rabi rainfall (Post_Monsoon + Winter)
    state_rain['Rabi_Rainfall_mm'] = state_rain['Post_Monsoon_Rainfall_mm'] + state_rain['Winter_Rainfall_mm']

    # Round rainfall figures
    for col in ['Annual_Rainfall_mm', 'Monsoon_Rainfall_mm', 'Post_Monsoon_Rainfall_mm', 'Winter_Rainfall_mm', 'Pre_Monsoon_Rainfall_mm', 'Rabi_Rainfall_mm']:
        state_rain[col] = state_rain[col].round(2)

    return state_rain

def integrate_datasets(crop_df, rain_df):
    print("\n--- 3. Integrating Crop and Rainfall Datasets ---")
    print(f"Clean crop records to merge: {len(crop_df):,}")
    print(f"State-level annual rainfall records: {len(rain_df):,}")

    # Merge crop records with state-level rainfall on State and Year
    combined = pd.merge(
        crop_df,
        rain_df,
        on=['State', 'Year'],
        how='left'
    )
    print(f"Combined dataset records after merge: {len(combined):,}")

    # Assign season-matched rainfall for each record
    # Kharif/Autumn -> Monsoon_Rainfall_mm
    # Rabi/Winter -> Rabi_Rainfall_mm
    # Summer -> Pre_Monsoon_Rainfall_mm
    # Whole Year / others -> Annual_Rainfall_mm
    conditions = [
        combined['Season'].isin(['Kharif', 'Autumn']),
        combined['Season'].isin(['Rabi', 'Winter']),
        combined['Season'] == 'Summer'
    ]
    choices = [
        combined['Monsoon_Rainfall_mm'],
        combined['Rabi_Rainfall_mm'],
        combined['Pre_Monsoon_Rainfall_mm']
    ]
    combined['Season_Rainfall_mm'] = np.select(conditions, choices, default=combined['Annual_Rainfall_mm'])
    combined['Season_Rainfall_mm'] = combined['Season_Rainfall_mm'].round(2)

    # Check join coverage
    missing_rain = combined['Annual_Rainfall_mm'].isna().sum()
    print(f"Records with unmatched rainfall: {missing_rain:,} ({(missing_rain/len(combined))*100:.2f}%)")

    return combined

def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    if not os.path.exists(RAW_CROP_PATH) or not os.path.exists(RAW_RAIN_PATH):
        print("Error: Raw files missing in datasets/raw/")
        sys.exit(1)

    # 1. Clean Crop Data
    clean_crop = clean_crop_data(RAW_CROP_PATH)
    print(f"Saving cleaned crop data to {CLEAN_CROP_PATH}...")
    clean_crop.to_csv(CLEAN_CROP_PATH, index=False)
    print(f"Clean crop data saved: {os.path.getsize(CLEAN_CROP_PATH):,} bytes")

    # 2. Clean Rainfall Data
    state_rainfall = clean_rainfall_data(RAW_RAIN_PATH)

    # 3. Integrate Datasets
    combined = integrate_datasets(clean_crop, state_rainfall)
    print(f"Saving integrated dataset to {COMBINED_PATH}...")
    combined.to_csv(COMBINED_PATH, index=False)
    print(f"Combined data saved: {os.path.getsize(COMBINED_PATH):,} bytes")

    print("\n--- 4. Summary & Verification ---")
    print(f"States in combined: {combined['State'].nunique()}")
    print(f"Districts in combined: {combined['District'].nunique()}")
    print(f"Crops in combined: {combined['Crop'].nunique()}")
    print(f"Years covered: {combined['Year'].min()} - {combined['Year'].max()}")
    print("Sample record:")
    print(combined[['State', 'District', 'Year', 'Season', 'Crop', 'Area', 'Production', 'Yield', 'Annual_Rainfall_mm', 'Season_Rainfall_mm']].head(3))
    print("\nData preprocessing completed successfully.")

if __name__ == "__main__":
    main()

