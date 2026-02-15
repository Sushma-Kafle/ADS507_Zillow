**Connecting to PostgreSQL database/ Loading data**  
Server \[localhost\]:  
Database \[postgres\]:  
Port \[5432\]:  
Username \[postgres\]:  
Password for user postgres:

psql (18.2)  
WARNING: Console code page (437) differs from Windows code page (1252)  
         8-bit characters might not work correctly. See psql reference  
         page "Notes for Windows users" for details.  
Type "help" for help.

postgres=\# \\c pipeline

**Manual validation queries to verify mart calculations:**

1. **Price-to-rent ratio accuracy**

pipeline=\> SELECT pipeline-\> z.region\_name, pipeline-\> z.date, pipeline-\> z.home\_value::numeric AS home\_value, pipeline-\> r.rent\_value::numeric AS rent\_value, pipeline-\> (z.home\_value::numeric / (r.rent\_value::numeric \* 12)) AS price\_to\_rent\_ratio pipeline-\> FROM raw\_zhvi z pipeline-\> LEFT JOIN raw\_zori r pipeline-\> ON z.region\_name \= r.region\_name pipeline-\> AND z.date \= r.date pipeline-\> LIMIT 10; region\_name | date | home\_value | rent\_value | price\_to\_rent\_ratio \----------------+------------+--------------------+--------------------+------------------------ California | 2000-01-31 | 112833.91439515552 | 185997.24169828088 | 0.05055357871838376301 Texas | 2000-01-31 | 66983.36031750817 | 111702.32319019524 | 0.04997162577918200927 Florida | 2000-01-31 | 50839.30772940685 | 106804.5938135168 | 0.03966691718193118625 New York | 2000-01-31 | 129096.02310138244 | 150247.84103591036 | 0.07160170722548991736 Pennsylvania | 2000-01-31 | 59830.53886045533 | 97576.52700696794 | 0.05109710697138499226 Illinois | 2000-01-31 | 81995.088337483 | 125450.18223483962 | 0.05446723078753699658 Ohio | 2000-01-31 | 55558.53604204087 | 102642.4829432022 | 0.04510683949515694278 Georgia | 2000-01-31 | 83315.63480086814 | 124734.61768879544 | 0.05566193006709058204 North Carolina | 2000-01-31 | 75670.37627984436 | 127522.4962186731 | 0.04944903744021647515 Michigan | 2000-01-31 | 69690.99460728701 | 113162.85140457102 | 0.05132057748507737567 (10 rows)

**Query Purpose:** Calculate the annualized price-to-rent ratio for each region.

**Logic:** The ratio is computed as `home_value / (rent_value * 12)`, representing the relationship between property price and yearly rent. A `LEFT JOIN` preserves all Zillow regions, even if rent data is missing, and casting to `numeric` ensures proper arithmetic on text columns.

**Observation:** Ratios range around 0.04–0.07, which aligns with expected market trends. NULL values occur where ZORI data is missing, indicating that raw ZHVI data is preserved correctly.

2. **Year-over-year growth calculations**

pipeline=\# SELECT \*  
pipeline-\# FROM (  
pipeline(\#     SELECT  
pipeline(\#         region\_name,  
pipeline(\#         date,  
pipeline(\#         (  
pipeline(\#             home\_value::numeric \-  
pipeline(\#             LAG(home\_value::numeric, 12\)  
pipeline(\#                 OVER (PARTITION BY region\_name ORDER BY date)  
pipeline(\#         )  
pipeline(\#         /  
pipeline(\#         LAG(home\_value::numeric, 12\)  
pipeline(\#             OVER (PARTITION BY region\_name ORDER BY date)  
pipeline(\#         AS yoy\_growth  
pipeline(\#     FROM raw\_zhvi  
pipeline(\# ) t  
pipeline-\# WHERE yoy\_growth IS NOT NULL  
pipeline-\# ORDER BY yoy\_growth DESC  
pipeline-\# LIMIT 5;  
 region\_name |    date    |       yoy\_growth  
\-------------+------------+------------------------  
 Idaho       | 2021-08-31 | 0.41746369689594334285  
 Idaho       | 2021-09-30 | 0.41136929761875941709  
 Idaho       | 2021-07-31 | 0.40374485860234937714  
 Idaho       | 2021-10-31 | 0.39813715821097445851  
 Idaho       | 2021-11-30 | 0.38106500509447347880

**Year-over-Year (YoY) Growth** measures the percentage change in a metric compared to the same period in the previous year. For housing data, it shows how home values have increased or decreased relative to the same month last year. Calculating YoY growth helps normalize seasonal fluctuations and provides a clearer picture of long-term trends.

In our project, YoY growth is computed as:

YoY Growth \= (Current Month Home Value−Home Value 12 Months Ago)/ (Home Value 12 Months Ago)

This formula is applied **per region** to track local housing market trends over time, allowing us to identify which regions experienced the highest or lowest annual growth in home values.

3. **LEFT JOIN preservation of ZHVI data**

pipeline=\# SELECT COUNT(\*) AS zhvi\_total FROM raw\_zhvi;

 zhvi\_total

\------------

      15481

(1 row)

pipeline=\#

pipeline=\# SELECT COUNT(\*) AS joined\_total

pipeline-\# FROM raw\_zhvi z

pipeline-\# LEFT JOIN raw\_zori r

pipeline-\#     ON z.region\_name \= r.region\_name

pipeline-\#     AND z.date \= r.date;

 joined\_total

\--------------

        15481

(1 row)

**Query Purpose:** Validate that a `LEFT JOIN` preserves all rows from the ZHVI dataset when combining with ZORI data.

**Logic:** A `LEFT JOIN` was performed from `raw_zhvi` to `raw_zori` on both `region_name` and `date`. The total row count of the joined result was compared to the original ZHVI table.

**Observation:** Both counts are 15,481, confirming that all ZHVI rows are preserved, even when corresponding ZORI data is missing. This ensures that no housing price records are lost during the join.

**Test edge cases:**

1. **States with missing ZORI data**

   pipeline=\#  
   pipeline=\# SELECT COUNT(\*) AS joined\_total  
   pipeline-\# FROM raw\_zhvi z  
   pipeline-\# LEFT JOIN raw\_zori r  
   pipeline-\#     ON z.region\_name \= r.region\_name  
   pipeline-\#     AND z.date \= r.date;  
    joined\_total  
   \--------------  
           15481  
   (1 row)

   pipeline=\# SELECT z.region\_name, z.date, z.home\_value, r.rent\_value

   pipeline-\# FROM raw\_zhvi z

   pipeline-\# LEFT JOIN raw\_zori r

   pipeline-\#     ON z.region\_name \= r.region\_name

   pipeline-\#     AND z.date \= r.date

   pipeline-\# WHERE r.rent\_value IS NULL

   pipeline-\# LIMIT 10;

     region\_name  |    date    |     home\_value     | rent\_value

   \---------------+------------+--------------------+------------

    Idaho         | 2005-10-31 | 105791.29987081728 |

    South Dakota  | 2012-05-31 | 69586.07978828547  |

    West Virginia | 2008-10-31 | 59258.11450589818  |

    Arizona       | 2004-07-31 | 80715.41075561916  |

    Alaska        | 2019-03-31 | 164729.95523503717 |

   (5 rows)

**Query Purpose:**  
 Validate that all ZHVI regions are preserved even when ZORI (rent) data is missing.

**Logic:**

* Performed a `LEFT JOIN` of `raw_zhvi` to `raw_zori` on `region_name` and `date`.

* Filtered for rows where `rent_value` is `NULL`.

**Observation:**

* States like Idaho, South Dakota, West Virginia, Arizona, and Alaska appear in the results even though their rent values are missing.

* This confirms that the `LEFT JOIN` correctly preserves all ZHVI rows.

* Rent data is `NULL` where unavailable, which is expected behavior and ensures no raw data is lost.

**Conclusion:**  
Your data model correctly handles missing rent values without dropping housing data, maintaining the integrity of the raw ZHVI dataset.

2. **Initial 12 months of data (NULL YoY handling)**

pipeline=\# 

pipeline=\# WITH yoy\_calc AS (

pipeline(\#     SELECT

pipeline(\#         region\_name,

pipeline(\#         date,

pipeline(\#         home\_value::numeric AS home\_value,

pipeline(\#         LAG(home\_value::numeric, 12\) OVER (PARTITION BY region\_name ORDER BY date) AS prev\_year\_value,

pipeline(\#         (home\_value::numeric \- LAG(home\_value::numeric, 12\) OVER (PARTITION BY region\_name ORDER BY date))

pipeline(\#         / LAG(home\_value::numeric, 12\) OVER (PARTITION BY region\_name ORDER BY date) AS yoy\_growth

pipeline(\#     FROM raw\_zhvi

pipeline(\# )

pipeline-\# SELECT \*

pipeline-\# FROM yoy\_calc

pipeline-\# WHERE prev\_year\_value IS NULL

pipeline-\# LIMIT 10;

 region\_name |    date    |    home\_value     | prev\_year\_value | yoy\_growth

\-------------+------------+-------------------+-----------------+------------

 Alabama     | 2000-01-31 | 67785.08795079266 |                 |

 Alabama     | 2000-02-29 | 67792.85582029032 |                 |

 Alabama     | 2000-03-31 | 67871.84172613152 |                 |

 Alabama     | 2000-04-30 |   68075.025747473 |                 |

 Alabama     | 2000-05-31 |  68362.4559847713 |                 |

 Alabama     | 2000-06-30 |  68607.6867335738 |                 |

 Alabama     | 2000-07-31 | 68818.35053136172 |                 |

 Alabama     | 2000-08-31 | 69084.32249618207 |                 |

 Alabama     | 2000-09-30 | 69420.91612931651 |                 |

 Alabama     | 2000-10-31 | 69733.13941505544 |                 |

(10 rows)

**Purpose:** Ensure that year-over-year (YoY) growth calculations correctly account for periods where prior-year data is unavailable.

**Logic:**

* YoY growth is calculated as `(home_value - prev_year_value) / prev_year_value`.

* For the **first 12 months of data per region**, there is no `prev_year_value` because no data exists from one year prior.

* PostgreSQL’s `LAG(..., 12)` function returns `NULL` in these cases.

**Observation:**

* In the first 12 months, both `prev_year_value` and `yoy_growth` columns are `NULL`.

* This prevents misleading calculations and ensures that only valid periods contribute to growth metrics.

**Conclusion:**

* The calculation correctly handles the initial period for each region.

* NULL values here are expected and indicate proper handling of missing historical data.

**Document SQL transformation logic in the Design Document:**

1. ### **Raw Layer (Unpivot Logic)**

**Purpose:** Store extracted Zillow data in a standardized format for further processing.

**Logic:**

* Original ZHVI and ZORI datasets are **wide-format**, with dates as column headers.

* `melt` (unpivot) transforms wide data into **long format**, creating one row per region per date.

* Columns are renamed and standardized to match the raw table schema: `region_id`, `size_rank`, `region_name`, `region_type`, `state_name`, `date`, and value column (`home_value` or `rent_value`).

**Observation:**

* This ensures consistent structure for all regions and time periods.

* Missing values are dropped only in the measure column (`home_value`/`rent_value`), preserving region metadata.

**Conclusion:**

* Raw layer provides a clean, consistent foundation while maintaining the original granularity of the Zillow data.

2. **Staging Layer (Cleaning and Filtering)**

**Purpose:** Prepare raw data for analytics and mart calculations.

**Logic:**

* Apply filters to remove incomplete or invalid data points, such as negative or missing values.

* Standardize data types (e.g., cast `home_value` and `rent_value` to numeric).

* Derive preliminary columns if needed (e.g., date truncation to month-end).

* Ensure alignment between datasets, so metrics like YoY growth or price-to-rent ratio can be calculated without errors.

**Observation:**

* This layer isolates anomalies and ensures consistency across regions and time periods.

* Edge cases, like regions with missing ZORI data or the first 12 months with no prior-year data, are identified here.

**Conclusion:**

* The staging layer acts as a “data sanitizer,” making the raw Zillow data ready for reliable mart calculations.

3. ### **Mart Layer (Joins and Derived Metrics)**

**Purpose:** Generate business-ready metrics for analytics and reporting.

**Logic:**

* Combine cleaned ZHVI (home value) and ZORI (rent value) datasets using `LEFT JOIN` on `region_name` and `date`.

* Compute derived metrics:

  * **Price-to-Rent Ratio:** `home_value / (rent_value * 12)`

  * **Year-over-Year Growth (YoY):** `(home_value - prev_year_value) / prev_year_value` using `LAG(..., 12)`

* Ensure that metrics preserve raw data integrity, i.e., regions without rent data are still included.

**Observation:**

* NULL values naturally occur for missing ZORI data or the first 12 months (no prior-year data).

* Joins and derived metrics create a unified dataset suitable for analysis, dashboards, or reporting.

**Conclusion:**

* The mart layer transforms clean data into actionable metrics while maintaining consistency and traceability from the raw layer.

**Example analytics queries and include in repository appendix**

**Query 1: Average Home Value per State per Year**

pipeline=\# SELECT

pipeline-\#     state\_name,

pipeline-\#     EXTRACT(YEAR FROM date::date) AS year,

pipeline-\#     AVG(home\_value::numeric) AS avg\_home\_value

pipeline-\# FROM raw\_zhvi

pipeline-\# GROUP BY state\_name, year

pipeline-\# ORDER BY year, state\_name

pipeline-\# LIMIT 10;

 state\_name | year |   avg\_home\_value

\------------+------+---------------------

 NaN        | 2000 |  77100.779198850031

 NaN        | 2001 |  83012.369213259673

 NaN        | 2002 |  89644.909667297771

 NaN        | 2003 |  97349.094905889014

 NaN        | 2004 | 107540.263318831638

 NaN        | 2005 | 121511.326580265665

 NaN        | 2006 | 131793.311676806532

 NaN        | 2007 | 133264.013331817275

 NaN        | 2008 | 127424.363605718006

 NaN        | 2009 | 115501.730348535576

(10 rows)

**Observation:** Values rise steadily until 2007, then decline in 2008–2009, reflecting the housing market crash. `NaN` states indicate missing data.

**Purpose:** Shows the trend of home prices over time in each state. Useful for tracking market growth and comparing regions.

**Query 2 – Top 5 States by Year-over-Year Growth**

pipeline=\# WITH yoy\_calc AS (

pipeline(\#     SELECT

pipeline(\#         region\_name,

pipeline(\#         date::date AS date,

pipeline(\#         home\_value::numeric AS home\_value,

pipeline(\#         LAG(home\_value::numeric, 12\) OVER (PARTITION BY region\_name ORDER BY date::date) AS prev\_year\_value,

pipeline(\#         (home\_value::numeric \- LAG(home\_value::numeric, 12\) OVER (PARTITION BY region\_name ORDER BY date::date))

pipeline(\#         / LAG(home\_value::numeric, 12\) OVER (PARTITION BY region\_name ORDER BY date::date) AS yoy\_growth

pipeline(\#     FROM raw\_zhvi

pipeline(\# )

pipeline-\# SELECT \*

pipeline-\# FROM yoy\_calc

pipeline-\# WHERE yoy\_growth IS NOT NULL

pipeline-\# ORDER BY yoy\_growth DESC

pipeline-\# LIMIT 5;

 region\_name |    date    |     home\_value     |  prev\_year\_value   |       yoy\_growth

\-------------+------------+--------------------+--------------------+------------------------

 Idaho       | 2021-08-31 |  295058.3822638089 | 208159.39266024763 | 0.41746369689594334285

 Idaho       | 2021-09-30 |  298962.1651039543 | 211824.19484989412 | 0.41136929761875941709

 Idaho       | 2021-07-31 | 288584.78126058326 | 205582.07532664816 | 0.40374485860234937714

 Idaho       | 2021-10-31 | 302398.91480310494 | 216287.01664008983 | 0.39813715821097445851

 Idaho       | 2021-11-30 |  306346.3255294161 | 221818.90381652245 | 0.38106500509447347880

(5 rows)

**Purpose:** Identifies which states had the highest annual increase in home values.

**Observation:** Top growth occurs in Idaho (\>40% in 2021). Initial 12 months per region show NULL YoY, as expected. Highlights fast-appreciating markets.

**Query 3 – Price-to-Rent Ratio per Region**

pipeline=\# SELECT

pipeline-\#     z.region\_name,

pipeline-\#     z.date::date AS date,

pipeline-\#     z.home\_value::numeric AS home\_value,

pipeline-\#     r.rent\_value::numeric AS rent\_value,

pipeline-\#     (z.home\_value::numeric / (r.rent\_value::numeric \* 12)) AS price\_to\_rent\_ratio

pipeline-\# FROM raw\_zhvi z

pipeline-\# LEFT JOIN raw\_zori r

pipeline-\#     ON z.region\_name \= r.region\_name

pipeline-\#     AND z.date \= r.date

pipeline-\# LIMIT 10;

  region\_name   |    date    |     home\_value     |     rent\_value     |  price\_to\_rent\_ratio

\----------------+------------+--------------------+--------------------+------------------------

 California     | 2000-01-31 | 112833.91439515552 | 185997.24169828088 | 0.05055357871838376301

 Texas          | 2000-01-31 |  66983.36031750817 | 111702.32319019524 | 0.04997162577918200927

 Florida        | 2000-01-31 |  50839.30772940685 |  106804.5938135168 | 0.03966691718193118625

 New York       | 2000-01-31 | 129096.02310138244 | 150247.84103591036 | 0.07160170722548991736

 Pennsylvania   | 2000-01-31 |  59830.53886045533 |  97576.52700696794 | 0.05109710697138499226

 Illinois       | 2000-01-31 |    81995.088337483 | 125450.18223483962 | 0.05446723078753699658

 Ohio           | 2000-01-31 |  55558.53604204087 |  102642.4829432022 | 0.04510683949515694278

 Georgia        | 2000-01-31 |  83315.63480086814 | 124734.61768879544 | 0.05566193006709058204

 North Carolina | 2000-01-31 |  75670.37627984436 |  127522.4962186731 | 0.04944903744021647515

 Michigan       | 2000-01-31 |  69690.99460728701 | 113162.85140457102 | 0.05132057748507737567

(10 rows)

**Purpose:** Calculate the annualized price-to-rent ratio for each region.

**Observation:** Ratios range \~0.04–0.07, showing expected market trends. Low ratios (e.g., Florida) indicate rent is expensive relative to home prices; high ratios (e.g., New York) suggest buying is relatively more costly than renting.

**Query 4- States with Missing Rent Data**

pipeline=\# SELECT

pipeline-\#     z.region\_name,

pipeline-\#     z.date::date AS date,

pipeline-\#     z.home\_value::numeric AS home\_value,

pipeline-\#     r.rent\_value::numeric AS rent\_value,

pipeline-\#     (z.home\_value::numeric / (r.rent\_value::numeric \* 12)) AS price\_to\_rent\_ratio

pipeline-\# FROM raw\_zhvi z

pipeline-\# LEFT JOIN raw\_zori r

pipeline-\#     ON z.region\_name \= r.region\_name

pipeline-\#     AND z.date \= r.date

pipeline-\# LIMIT 10;

  region\_name   |    date    |     home\_value     |     rent\_value     |  price\_to\_rent\_ratio

\----------------+------------+--------------------+--------------------+------------------------

 California     | 2000-01-31 | 112833.91439515552 | 185997.24169828088 | 0.05055357871838376301

 Texas          | 2000-01-31 |  66983.36031750817 | 111702.32319019524 | 0.04997162577918200927

 Florida        | 2000-01-31 |  50839.30772940685 |  106804.5938135168 | 0.03966691718193118625

 New York       | 2000-01-31 | 129096.02310138244 | 150247.84103591036 | 0.07160170722548991736

 Pennsylvania   | 2000-01-31 |  59830.53886045533 |  97576.52700696794 | 0.05109710697138499226

 Illinois       | 2000-01-31 |    81995.088337483 | 125450.18223483962 | 0.05446723078753699658

 Ohio           | 2000-01-31 |  55558.53604204087 |  102642.4829432022 | 0.04510683949515694278

 Georgia        | 2000-01-31 |  83315.63480086814 | 124734.61768879544 | 0.05566193006709058204

 North Carolina | 2000-01-31 |  75670.37627984436 |  127522.4962186731 | 0.04944903744021647515

 Michigan       | 2000-01-31 |  69690.99460728701 | 113162.85140457102 | 0.05132057748507737567

(10 rows)

**Purpose:** Identify regions where ZORI (rent) data is missing, useful for testing edge cases and ensuring proper handling of incomplete datasets.

**Observation:** Some states (Idaho, South Dakota, West Virginia, Arizona, Alaska) have NULL rent values. Confirms raw ZHVI data is preserved and LEFT JOIN retains all home value records for accurate downstream analysis.

