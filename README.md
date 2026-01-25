# Zillow Housing Data ETL Pipeline

An automated data pipeline for extracting, transforming, and loading Zillow housing market data using Apache Airflow, PostgreSQL, and Docker.

## Project Structure

```
├── docker-compose.yml          # Docker services configuration
├── airflow/                    # Airflow DAGs and configs
│   └── dags/
│       └── zillow_etl.py       # Main ETL pipeline DAG
├── etl/                        # ETL Python modules
│   ├── extract.py              # Data extraction from Zillow
│   ├── load.py                 # Data loading to PostgreSQL
│   └── requirements.txt        # Python dependencies
├── sql/                        # Database SQL scripts
│   ├── 01_raw_tables.sql       # Raw layer table definitions
│   ├── 02_staging.sql          # Staging transformations
│   └── 03_marts.sql            # Analytics data marts
├── docs/                       # Documentation
│   ├── architecture.png        # System architecture diagram
│   └── design_doc.pdf          # Detailed design document
└── README.md                   # This file
```

## Zillow Research Data

This pipeline extracts housing market data from [Zillow Research](https://www.zillow.com/research/data/), which provides free, publicly available housing data.

### Available Datasets

#### ZHVI (Zillow Home Value Index)

The Zillow Home Value Index (ZHVI) is a smoothed, seasonally adjusted measure of the typical home value and market changes across a given region and housing type.

| Dataset | Description | Geographic Levels |
|---------|-------------|-------------------|
| All Homes | Typical value for all home types (35th-65th percentile) | Metro, State, County, City, ZIP |
| Single Family | Typical value for single-family residences | Metro, State |
| Condo/Co-op | Typical value for condominiums and co-ops | Metro, State |
| Top-Tier | Typical value (65th-95th percentile) | Metro, State |
| Bottom-Tier | Typical value (5th-35th percentile) | Metro, State |

**Current Statistics (2025):**
- Typical U.S. home value: ~$368,000

#### ZORI (Zillow Observed Rent Index)

The Zillow Observed Rent Index (ZORI) is a smoothed measure of the typical observed market rate rent across a given region.

| Dataset | Description | Geographic Levels |
|---------|-------------|-------------------|
| All Homes | Typical rent for all home types (40th-60th percentile) | Metro, State, County, City, ZIP |

**Current Statistics (2025):**
- National rent index: ~$2,049/month
- Annual rent growth: ~3-4%

### Data Characteristics

- **Update Frequency:** Monthly
- **Historical Data:** Available from 2000 onwards
- **Format:** CSV files with wide format (dates as columns)
- **Data Quality:** Smoothed and seasonally adjusted

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ADS507_FinalProject
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Access the Airflow UI:
   - URL: http://localhost:8080
   - Username: `admin`
   - Password: `admin`

4. Enable and trigger the `zillow_etl_pipeline` DAG

### Services

| Service | Port | Description |
|---------|------|-------------|
| Airflow Webserver | 8080 | Airflow web UI |
| PostgreSQL | 5432 | Database server |

## Data Architecture

### Layer 1: Raw (Bronze)

Raw data as extracted from Zillow without modifications.

- `raw.raw_zhvi` - Home value index data
- `raw.raw_zori` - Rental index data

### Layer 2: Staging (Silver)

Cleaned and transformed data in long format.

- `staging.stg_zhvi` - Unpivoted home values
- `staging.stg_zori` - Unpivoted rental values
- `staging.dim_geography` - Geographic dimension
- `staging.dim_date` - Date dimension

### Layer 3: Marts (Gold)

Analytics-ready tables and views.

- `marts.fact_home_values` - Home value facts with MoM/YoY changes
- `marts.fact_rental_values` - Rental value facts with MoM/YoY changes
- `marts.vw_metro_home_values` - Metro-level home value trends
- `marts.vw_metro_rentals` - Metro-level rental trends
- `marts.vw_price_to_rent` - Price-to-rent ratio analysis
- `marts.vw_affordability_index` - Affordability metrics

## ETL Pipeline

The Airflow DAG `zillow_etl_pipeline` orchestrates the following tasks:

```
[extract_zhvi] ──► [load_zhvi_to_raw] ──┐
                                        ├──► [transform_to_staging] ──► [build_data_marts] ──► [data_quality_check]
[extract_zori] ──► [load_zori_to_raw] ──┘
```

### Schedule

The pipeline runs monthly to align with Zillow's data update frequency.

## Development

### Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r etl/requirements.txt
   ```

3. Run extraction tests:
   ```bash
   python etl/extract.py
   ```

### Running Tests

```bash
pytest tests/ -v
```

## Data Sources

- **Zillow Research:** https://www.zillow.com/research/data/
- **Methodology - ZHVI:** https://www.zillow.com/research/methodology-neural-zhvi-32128/
- **Methodology - ZORI:** https://www.zillow.com/research/methodology-zori-repeat-rent-27092/

## License

This project is for educational purposes. Zillow data is subject to Zillow's terms of use.
