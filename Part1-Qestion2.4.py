import geopandas as gpd
import pandas as pd
import numpy as np

from pathlib import Path
from loguru import logger

PROJECT = Path(
    r"C:\Users\USER\Desktop\Technical Assessment\All Dataset"
)

OUTPUT = PROJECT / "outputs"
TABLES = OUTPUT / "tables"

wards = gpd.read_file(
    OUTPUT / "ward_accessibility.gpkg"
)

import geopandas as gpd
import pandas as pd
import numpy as np

from pathlib import Path
from loguru import logger

PROJECT = Path(
    r"C:\Users\USER\Desktop\Technical Assessment\All Dataset"
)

OUTPUT = PROJECT / "outputs"
TABLES = OUTPUT / "tables"

wards = gpd.read_file(
    OUTPUT / "ward_accessibility.gpkg"
)

facilities = gpd.read_file(
    OUTPUT / "facility_accessibility.gpkg"
)

facilities = gpd.read_file(
    OUTPUT / "facility_accessibility.gpkg"
)

# Detect Required Fields

def detect(df, keywords):

    for keyword in keywords:

        for column in df.columns:

            if keyword.lower() in column.lower():

                return column

    raise ValueError(
        f"Unable to locate {keywords}"
    )

distance_field = detect(
    wards,
    ["distance"]
)

nearest_field = detect(
    wards,
    ["nearest"]
)

score_field = detect(
    facilities,
    ["score", "readiness", "staff"]
)

# Join Facility Readiness to Wards

facility_scores = facilities[
    [nearest_field, score_field]
].copy()

wards = wards.merge(
    facility_scores,
    left_on=nearest_field,
    right_on=nearest_field,
    how="left"
)

wards[score_field] = wards[score_field].fillna(0)

# Define Thresholds

MAX_DISTANCE = 10000      # metres

MIN_READINESS = 0.70

# Classify Service Gaps

def classify_gap(row):

    distance = row[distance_field]

    readiness = row[score_field]

    if pd.isna(distance):

        return "No Access"

    if distance > MAX_DISTANCE:

        return "Geographic Gap"

    if readiness < MIN_READINESS:

        return "Staffing Gap"

    return "Well Served"

wards["service_gap"] = wards.apply(
    classify_gap,
    axis=1
)

# Priority Ranking

priority = {

    "No Access": 1,

    "Geographic Gap": 2,

    "Staffing Gap": 3,

    "Well Served": 4

}

wards["priority_rank"] = (

    wards["service_gap"]

    .map(priority)

)

# Summary Statistics

summary = (

    wards

    .groupby("service_gap")

    .size()

    .reset_index(name="Number_of_Wards")

)

print(summary)

# Population summary

population_field = detect(
    wards,
    ["population", "pop"]
)

population_summary = (

    wards

    .groupby("service_gap")

    .agg(

        Wards=("service_gap", "count"),

        Population=(population_field, "sum")

    )

    .reset_index()

)

# Export Results

wards.to_file(

    OUTPUT / "service_gap_analysis.gpkg",

    driver="GPKG"

)

wards.drop(

    columns="geometry",

    errors="ignore"

).to_csv(

    TABLES / "service_gap_analysis.csv",

    index=False

)

summary.to_csv(

    TABLES / "service_gap_summary.csv",

    index=False

)

population_summary.to_csv(

    TABLES / "service_gap_population_summary.csv",

    index=False

)

logger.success("Question 2.4 completed.")

