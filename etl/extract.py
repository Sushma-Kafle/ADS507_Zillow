"""
Zillow Data Extraction Module

This module handles the extraction of housing data from local CSV files
originally sourced from Zillow Research: https://www.zillow.com/research/data/

Available datasets:
- ZHVI (Zillow Home Value Index): Typical home values (metro-level)
- ZORI (Zillow Observed Rent Index): Typical rental prices (metro-level)
"""

import os
import pandas as pd
from typing import Tuple


# Local CSV file paths (mounted into the container via docker-compose)
DATA_DIR = os.getenv("DATA_DIR", "/opt/airflow/data")
ZHVI_FILE = os.path.join(DATA_DIR, "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv")
ZORI_FILE = os.path.join(DATA_DIR, "Metro_zori_uc_sfrcondomfr_sm_sa_month.csv")


def extract_zhvi() -> pd.DataFrame:
    """
    Load ZHVI (Zillow Home Value Index) data from local CSV.

    Returns:
        pd.DataFrame: Wide-format DataFrame with monthly home values as columns
    """
    print(f"Loading ZHVI data from {ZHVI_FILE}")
    df = pd.read_csv(ZHVI_FILE)
    print(f"✓ Loaded ZHVI data: {len(df)} rows, {len(df.columns)} columns")
    return df


def extract_zori() -> pd.DataFrame:
    """
    Load ZORI (Zillow Observed Rent Index) data from local CSV.

    Returns:
        pd.DataFrame: Wide-format DataFrame with monthly rent values as columns
    """
    print(f"Loading ZORI data from {ZORI_FILE}")
    df = pd.read_csv(ZORI_FILE)
    print(f"✓ Loaded ZORI data: {len(df)} rows, {len(df.columns)} columns")
    return df


def extract_all() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load both ZHVI and ZORI datasets from local CSVs.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (zhvi_df, zori_df)
    """
    zhvi_df = extract_zhvi()
    zori_df = extract_zori()
    return zhvi_df, zori_df
