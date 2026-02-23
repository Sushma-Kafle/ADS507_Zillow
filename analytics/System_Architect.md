# System Architecture Overview

The system architecture follows a modern layered data pipeline design that separates ingestion, transformation, and analytics responsibilities. Zillow’s publicly available ZHVI and ZORI datasets are ingested as raw CSV files and loaded into the PostgreSQL raw schema without modification, preserving the original source structure. The staging schema performs structural transformations, including wide-to-long unpivoting, normalization to one state per month, and preparation of standardized analytical fields (region_id, state, date, value). 

The mart layer computes derived business metrics such as price-to-rent ratio and year-over-year home value growth using window functions (e.g., LAG 12). Business intelligence tools (Metabase, Power BI, Tableau) connect exclusively to curated mart tables, ensuring stable analytics-ready datasets while insulating dashboards from upstream schema changes. 

This layered architecture enhances scalability, reproducibility, data quality, and long-term maintainability of housing market analytics.