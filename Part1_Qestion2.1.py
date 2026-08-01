# ==========================================================
# INSTALL REQUIRED LIBRARIES (Run Once)
# ==========================================================

import pandas
import geopandas
import networkx
import shapely
import scipy
import pyogrio
import rapidfuzz
import loguru

print("Everything installed successfully!")

"""
===============================================================
Question 2.1
Normalize LGA–Senatorial District Spreadsheet

Technical Assessment
Author: Your Name

This script automatically:

1. Reads the raw Excel workbook
2. Repairs merged cells
3. Cleans administrative names
4. Matches names against official boundaries
5. Creates a normalized lookup table
6. Generates reconciliation reports

No manual editing is required.
===============================================================
"""

import re
from pathlib import Path

import geopandas as gpd
import pandas as pd
from loguru import logger
from rapidfuzz import process

# ===============================================================
# PROJECT PATHS
# ===============================================================

PROJECT = Path(
    r"C:\Users\USER\Desktop\Technical Assessment\All Dataset"
)

OUTPUT = PROJECT / "outputs"
TABLES = OUTPUT / "tables"

OUTPUT.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

# ===============================================================
# INPUT FILES
# ===============================================================

EXCEL_FILE = PROJECT / "LGA_SEN_Districts.xlsx"
ADMIN_FILE = PROJECT / "admin_boundaries.gpkg"

# ===============================================================
# LOAD DATA
# ===============================================================

logger.info("Loading datasets...")

admin = gpd.read_file(ADMIN_FILE)

xls = pd.ExcelFile(EXCEL_FILE)

logger.success(f"Workbook contains {len(xls.sheet_names)} sheet(s).")

# ===============================================================
# READ FIRST SHEET
# ===============================================================

df = pd.read_excel(
    EXCEL_FILE,
    sheet_name=xls.sheet_names[0],
    header=None
)

logger.info(f"Rows loaded : {len(df):,}")

# ===============================================================
# REPAIR MERGED CELLS
# ===============================================================

df = df.ffill()

# ===============================================================
# REMOVE EMPTY ROWS/COLUMNS
# ===============================================================

df = df.dropna(axis=0, how="all")
df = df.dropna(axis=1, how="all")

logger.info(f"Rows after cleaning : {len(df):,}")

# ===============================================================
# PROMOTE FIRST ROW TO HEADER
# ===============================================================

df.columns = df.iloc[0]

df = df.iloc[1:].reset_index(drop=True)

# ===============================================================
# COLUMN DETECTION
# ===============================================================

def detect_column(columns, keywords):

    for keyword in keywords:

        for column in columns:

            if keyword.lower() in str(column).lower():

                return column

    raise ValueError(
        f"Unable to detect column containing {keywords}"
    )


lga_column = detect_column(
    df.columns,
    ["lga"]
)

senatorial_column = detect_column(
    df.columns,
    ["sen"]
)

logger.success("Administrative columns detected.")

# ===============================================================
# CLEAN TEXT
# ===============================================================

def clean_text(value):

    if pd.isna(value):

        return None

    value = str(value)

    value = value.upper()

    value = value.strip()

    value = value.replace("-", " ")

    value = value.replace("_", " ")

    value = value.replace(".", "")

    value = re.sub(r"\s+", " ", value)

    return value


df[lga_column] = df[lga_column].apply(clean_text)

df[senatorial_column] = df[senatorial_column].apply(clean_text)

# ===============================================================
# DETECT OFFICIAL LGA FIELD
# ===============================================================

admin_field = None

for col in admin.columns:

    if "lga" in col.lower():

        admin_field = col
        break

if admin_field is None:

    raise ValueError(
        "Unable to locate the LGA field in admin_boundaries.gpkg"
    )

official_lgas = (

    admin[admin_field]

    .astype(str)

    .apply(clean_text)

    .drop_duplicates()

    .tolist()

)

logger.success(
    f"{len(official_lgas)} official LGAs detected."
)

# ===============================================================
# FUZZY MATCHING
# ===============================================================

matched_names = []

reconciliation = []

unresolved = []

for lga in df[lga_column]:

    result = process.extractOne(
        lga,
        official_lgas,
        score_cutoff=85
    )

    if result:

        matched_names.append(result[0])

        reconciliation.append({

            "Original_Name": lga,
            "Matched_Name": result[0],
            "Similarity_Score": result[1]

        })

    else:

        matched_names.append(None)

        unresolved.append(lga)

df["LGA_STANDARD"] = matched_names

# ===============================================================
# NORMALIZED LOOKUP TABLE
# ===============================================================

lookup = (

    df[
        [
            "LGA_STANDARD",
            senatorial_column
        ]
    ]

    .rename(

        columns={

            senatorial_column:
            "SENATORIAL_DISTRICT"

        }

    )

    .drop_duplicates()

    .sort_values(
        "LGA_STANDARD"
    )

    .reset_index(drop=True)

)

lookup.insert(

    0,

    "LOOKUP_ID",

    range(1, len(lookup) + 1)

)

# ===============================================================
# EXPORTS
# ===============================================================

lookup.to_csv(

    TABLES / "lga_senatorial_lookup.csv",

    index=False

)

pd.DataFrame(
    reconciliation
).to_csv(

    TABLES / "name_reconciliation_report.csv",

    index=False

)

pd.DataFrame(

    {

        "UNRESOLVED_NAME": unresolved

    }

).to_csv(

    TABLES / "unresolved_names.csv",

    index=False

)

# ===============================================================
# SUMMARY
# ===============================================================

logger.success("Normalization completed successfully.")

print("\n==============================")
print("QUESTION 2.1 COMPLETED")
print("==============================")
print(f"Lookup Records      : {len(lookup):,}")
print(f"Reconciled Names    : {len(reconciliation):,}")
print(f"Unresolved Names    : {len(unresolved):,}")
print(f"Output Folder       : {TABLES}")

print("==============================")

import sqlite3
from pathlib import Path

