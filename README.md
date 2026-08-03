# eHA Technical Assessment – Senior Coordinator, Data and GIS Analytics

## Overview

This repository contains my submission for the **eHealth Africa (eHA) Senior Coordinator, Data and GIS Analytics Technical Assessment**.

The project demonstrates an end-to-end geospatial data engineering and spatial analysis workflow using Python. It automates data preparation, normalization, spatial database creation, accessibility modelling, service gap analysis, and the production of publication-quality maps.

The workflow was designed to be reproducible, modular, and scalable, following GIS and data engineering best practices.

---

# Project Objectives

The assessment addresses the following objectives:

* Automate the processing of raw spatial and tabular datasets.
* Normalize administrative boundary information.
* Build a governed spatial database with referential integrity.
* Analyse health facility accessibility using road networks.
* Identify underserved populations and service gaps.
* Produce publication-quality maps and analytical outputs.

---

# Repository Structure

```text
Technical Assessment/

│
├── data/
│   ├── raw/
│   └── processed/
│
├── outputs/
│   ├── database/
│   ├── figures/
│   └── tables/
│
├── src/
│   ├── 01_data_inventory.py
│   ├── 02_normalize_senatorial_lookup.py
│   ├── 03_build_spatial_database.py
│   ├── 04_population_accessibility.py
│   ├── 05_service_gap_analysis.py
│   └── 06_generate_maps.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

# Workflow

The analytical workflow follows six major stages:

## 1. Data Inventory

* Automatically scans all datasets
* Detects schemas
* Documents metadata
* Generates a data inventory

Outputs:

* data_inventory.csv
* data_dictionary.csv

---

## 2. Administrative Data Normalization

Automatically:

* Repairs merged Excel cells
* Cleans inconsistent names
* Standardizes administrative units
* Performs fuzzy matching
* Produces reconciliation reports

Outputs:

* lga_senatorial_lookup.csv
* name_reconciliation_report.csv
* unresolved_names.csv

---

## 3. Spatial Database Construction

Creates a governed spatial database containing:

* Administrative boundaries
* LGAs
* Senatorial districts
* Health facilities

Features include:

* Primary keys
* Foreign keys
* Declared CRS
* Spatial indexes
* Referential integrity

Output:

* technical_assessment.db

---

## 4. Population Accessibility Analysis

Computes accessibility using:

* Road network
* Ward population
* Facility locations
* Network travel distance

Outputs:

* ward_accessibility.csv
* ward_accessibility.gpkg

---

## 5. Service Gap Analysis

Classifies each ward into:

* Well Served
* Staffing Gap
* Geographic Gap
* No Access

Outputs:

* service_gap_analysis.csv
* service_gap_summary.csv
* service_gap_analysis.gpkg

---

## 6. Cartographic Outputs

Generates publication-quality maps including:

* Accessibility classification
* Health facilities
* Road network
* Administrative boundaries
* Scale bar
* North arrow
* Legend

Outputs:

* Accessibility_Map.png
* Accessibility_Map_A3.pdf

---

# Software Requirements

* Python 3.12
* Git
* GDAL-compatible GeoPandas installation

---

# Python Libraries

Required packages include:

* pandas
* geopandas
* numpy
* scipy
* networkx
* shapely
* pyproj
* pyogrio
* fiona
* rtree
* matplotlib
* openpyxl
* rapidfuzz
* loguru

Install using:

```bash
pip install -r requirements.txt
```

---

# Running the Project

Run the scripts in the following order:

```text
01_data_inventory.py

↓

02_normalize_senatorial_lookup.py

↓

03_build_spatial_database.py

↓

04_population_accessibility.py

↓

05_service_gap_analysis.py

↓

06_generate_maps.py
```

Each script produces outputs used by the subsequent stage.

---

# Methodology

The project follows a reproducible GIS workflow consisting of:

1. Automated data ingestion
2. Data quality assessment
3. Administrative data normalization
4. Spatial database construction
5. Road network analysis
6. Population-weighted accessibility modelling
7. Service gap classification
8. Cartographic visualization

---

# Outputs

The repository generates:

* Normalized lookup tables
* Spatial database
* Accessibility datasets
* Service gap reports
* Publication-quality maps
* Summary statistics

---

# Note

* All datasets are projected to a common Coordinate Reference System (CRS) before spatial analysis.
* Administrative names are standardized using automated cleaning and fuzzy matching.
* Road-network accessibility is used instead of straight-line (Euclidean) distance where applicable.
* Thresholds for accessibility and staffing can be adjusted based on programme requirements.

---

# Reproducibility

The workflow is fully reproducible.

No manual editing of source datasets is required.

All processing is automated through Python scripts.

---

# Author

**Name:** Oluseye Abraham

**Email:** [seyeabrahams@yahoo.com](seyeabrahams@yahoo.com)

**GitHub:** https://github.com/seyeabrahams

---

# License

This repository is submitted as part of a technical assessment for the **Senior Coordinator – Data and GIS Analytics** position at **eHealth Africa (eHA)**.

Unless otherwise stated, the contents are intended solely for assessment and demonstration purposes.
