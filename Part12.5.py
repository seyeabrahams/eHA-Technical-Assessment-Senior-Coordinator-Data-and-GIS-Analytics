"""
=============================================================
PART 1 – QUESTION 2.5

Generate Publication Quality Accessibility Map

Outputs
-------
1. Accessibility_Map.png
2. Accessibility_Map_A3.pdf
3. Map_Summary_Table.csv

Author: Your Name
=============================================================
"""

# ==========================================================
# IMPORT LIBRARIES
# ==========================================================

from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from loguru import logger

# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT = Path(
    r"C:\Users\USER\Desktop\Technical Assessment\All Dataset"
)

OUTPUT = PROJECT / "outputs"
FIGURES = OUTPUT / "figures"
TABLES = OUTPUT / "tables"

FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

# ==========================================================
# INPUT FILES
# ==========================================================

WARD_FILE = OUTPUT / "service_gap_analysis.gpkg"
ROAD_FILE = PROJECT / "road_network.geojson"
ADMIN_FILE = PROJECT / "admin_boundaries.gpkg"
FACILITY_FILE = PROJECT / "health_facilities.csv"

# ==========================================================
# CHECK FILES
# ==========================================================

files = [
    WARD_FILE,
    ROAD_FILE,
    ADMIN_FILE,
    FACILITY_FILE,
]

for f in files:
    if not f.exists():
        raise FileNotFoundError(f"Missing file:\n{f}")

logger.success("All required datasets found.")

# ==========================================================
# LOAD DATA
# ==========================================================

wards = gpd.read_file(WARD_FILE)
roads = gpd.read_file(ROAD_FILE)
admin = gpd.read_file(ADMIN_FILE)

facilities = pd.read_csv(FACILITY_FILE)

# ==========================================================
# AUTO DETECT COORDINATE FIELDS
# ==========================================================

def detect(df, keywords):

    for key in keywords:

        for col in df.columns:

            if key.lower() in col.lower():

                return col

    raise ValueError(f"Cannot detect column: {keywords}")

lon = detect(facilities, ["longitude", "lon", "x"])
lat = detect(facilities, ["latitude", "lat", "y"])

# ==========================================================
# CONVERT FACILITIES TO GEODATAFRAME
# ==========================================================

facility_gdf = gpd.GeoDataFrame(

    facilities,

    geometry=gpd.points_from_xy(

        facilities[lon],

        facilities[lat]

    ),

    crs="EPSG:4326"

)

facility_gdf = facility_gdf.to_crs(wards.crs)

roads = roads.to_crs(wards.crs)
admin = admin.to_crs(wards.crs)

# ==========================================================
# VERIFY SERVICE GAP FIELD
# ==========================================================

if "service_gap" not in wards.columns:

    raise ValueError(
        "Column 'service_gap' not found.\n"
        "Run Question 2.4 first."
    )

# ==========================================================
# COLOUR SCHEME
# ==========================================================

colors = {

    "Well Served": "#2E8B57",

    "Staffing Gap": "#FDB813",

    "Geographic Gap": "#E74C3C",

    "No Access": "#7F0000"

}

# ==========================================================
# CREATE FIGURE
# ==========================================================

fig, ax = plt.subplots(
    figsize=(16.54, 11.69)
)

# ==========================================================
# DRAW LAYERS
# ==========================================================

roads.plot(
    ax=ax,
    color="lightgrey",
    linewidth=0.4,
    zorder=1
)

admin.boundary.plot(
    ax=ax,
    color="black",
    linewidth=0.5,
    zorder=2
)

for category, colour in colors.items():

    subset = wards[wards["service_gap"] == category]

    if len(subset):

        subset.plot(
            ax=ax,
            color=colour,
            edgecolor="black",
            linewidth=0.15,
            zorder=3
        )

facility_gdf.plot(
    ax=ax,
    marker="^",
    color="navy",
    markersize=35,
    edgecolor="white",
    linewidth=0.4,
    zorder=4
)

# ==========================================================
# LEGEND
# ==========================================================

legend = []

for category, colour in colors.items():

    legend.append(

        mpatches.Patch(

            color=colour,

            label=category

        )

    )

legend.append(

    Line2D(

        [0],

        [0],

        marker="^",

        linestyle="",

        color="navy",

        markersize=8,

        label="Health Facility"

    )

)

ax.legend(

    handles=legend,

    title="Service Gap",

    loc="lower left",

    fontsize=9

)

# ==========================================================
# NORTH ARROW
# ==========================================================

ax.annotate(

    "N",

    xy=(0.96, 0.90),

    xytext=(0.96, 0.80),

    xycoords="axes fraction",

    ha="center",

    fontsize=16,

    fontweight="bold",

    arrowprops=dict(

        facecolor="black",

        width=4,

        headwidth=12

    )

)

# ==========================================================
# SCALE BAR (10 km)
# ==========================================================

xmin, xmax = ax.get_xlim()
ymin, ymax = ax.get_ylim()

x = xmin + 5000
y = ymin + 5000

scale = 10000

ax.plot(
    [x, x + scale],
    [y, y],
    color="black",
    linewidth=3
)

ax.text(
    x,
    y - 1200,
    "0",
    fontsize=8
)

ax.text(
    x + scale,
    y - 1200,
    "10 km",
    fontsize=8
)

# ==========================================================
# TITLE
# ==========================================================

plt.title(

    "Health Facility Accessibility and Service Gap Assessment",

    fontsize=18,

    weight="bold"

)

# ==========================================================
# REMOVE AXES
# ==========================================================

ax.set_axis_off()

# ==========================================================
# SAVE MAPS
# ==========================================================

png = FIGURES / "Accessibility_Map.png"

pdf = FIGURES / "Accessibility_Map_A3.pdf"

plt.savefig(
    png,
    dpi=300,
    bbox_inches="tight"
)

plt.savefig(
    pdf,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================================
# SUMMARY TABLE
# ==========================================================

summary = (

    wards

    .groupby("service_gap")

    .size()

    .reset_index(name="Number_of_Wards")

)

summary.to_csv(

    TABLES / "Map_Summary_Table.csv",

    index=False

)

# ==========================================================
# FINISHED
# ==========================================================

print("\n" + "=" * 60)
print("QUESTION 2.5 COMPLETED SUCCESSFULLY")
print("=" * 60)
print(f"PNG Map : {png}")
print(f"PDF Map : {pdf}")
print(f"Summary : {TABLES/'Map_Summary_Table.csv'}")
print("=" * 60)