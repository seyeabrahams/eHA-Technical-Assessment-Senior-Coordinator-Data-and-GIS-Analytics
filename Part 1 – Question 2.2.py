"""
==============================================================
Part 1 – Question 2.2

Build a Governed Spatial Database

Creates a relational SQLite database with:

• Declared CRS
• Primary Keys
• Foreign Keys
• Spatial Geometry (WKT)
• Attribute Indexes
• Spatial Indexes (bounding-box columns)
==============================================================
"""
import geopandas as gpd
import pandas as pd
from loguru import logger

# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT = Path(
    r"C:\Users\USER\Desktop\Technical Assessment\All Dataset"
)

OUTPUT = PROJECT / "outputs"
DB_FOLDER = OUTPUT / "database"

OUTPUT.mkdir(exist_ok=True)
DB_FOLDER.mkdir(exist_ok=True)

DATABASE = DB_FOLDER / "technical_assessment.db"

# ==========================================================
# INPUT DATA
# ==========================================================

ADMIN = PROJECT / "admin_boundaries.gpkg"
FACILITIES = PROJECT / "health_facilities.csv"
LOOKUP = OUTPUT / "tables" / "lga_senatorial_lookup.csv"

# ==========================================================
# CONNECT DATABASE
# ==========================================================

logger.info("Creating database...")

conn = sqlite3.connect(DATABASE)

conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

# ==========================================================
# LOAD DATA
# ==========================================================

admin = gpd.read_file(ADMIN)

facilities = pd.read_csv(FACILITIES)

lookup = pd.read_csv(LOOKUP)

# ==========================================================
# DETECT FIELDS
# ==========================================================

def detect(columns, keywords):

    for keyword in keywords:

        for column in columns:

            if keyword.lower() in column.lower():

                return column

    raise Exception(f"Cannot locate {keywords}")

ward_field = detect(admin.columns, ["ward"])
lga_field = detect(admin.columns, ["lga"])
state_field = detect(admin.columns, ["state"])

facility_lga = detect(facilities.columns, ["lga"])

lon_field = detect(
    facilities.columns,
    ["longitude", "lon", "x"]
)

lat_field = detect(
    facilities.columns,
    ["latitude", "lat", "y"]
)

# ==========================================================
# CRS
# ==========================================================

crs = admin.crs.to_string()

cursor.execute("""

CREATE TABLE IF NOT EXISTS CRS_METADATA (

    CRS_ID INTEGER PRIMARY KEY,

    CRS_NAME TEXT,

    CRS_STRING TEXT

)

""")

cursor.execute("""

INSERT INTO CRS_METADATA
VALUES
(
1,
'Administrative CRS',
?
)

""", (crs,))

# ==========================================================
# SENATORIAL DISTRICT
# ==========================================================

cursor.execute("""

CREATE TABLE SenatorialDistrict(

SenatorialID INTEGER PRIMARY KEY,

Name TEXT UNIQUE

)

""")

districts = lookup["SENATORIAL_DISTRICT"].drop_duplicates()

for i, name in enumerate(districts, 1):

    cursor.execute(

        """

        INSERT INTO SenatorialDistrict

        VALUES (?,?)

        """,

        (i, name)

    )

# ==========================================================
# LGA
# ==========================================================

cursor.execute("""

CREATE TABLE LGA(

LGA_ID INTEGER PRIMARY KEY,

LGA_NAME TEXT UNIQUE,

SenatorialID INTEGER,

FOREIGN KEY(SenatorialID)

REFERENCES SenatorialDistrict(SenatorialID)

)

""")

for _, row in lookup.iterrows():

    sid = cursor.execute(

        """

        SELECT SenatorialID

        FROM SenatorialDistrict

        WHERE Name=?

        """,

        (row["SENATORIAL_DISTRICT"],)

    ).fetchone()[0]

    cursor.execute(

        """

        INSERT INTO LGA

        (LGA_NAME,SenatorialID)

        VALUES (?,?)

        """,

        (

            row["LGA_STANDARD"],

            sid

        )

    )

# ==========================================================
# WARDS
# ==========================================================

cursor.execute("""

CREATE TABLE Ward(

WardID INTEGER PRIMARY KEY,

WardName TEXT,

LGA_ID INTEGER,

Geometry TEXT,

MinX REAL,

MinY REAL,

MaxX REAL,

MaxY REAL,

FOREIGN KEY(LGA_ID)

REFERENCES LGA(LGA_ID)

)

""")

for idx, row in admin.iterrows():

    lga = row[lga_field]

    result = cursor.execute(

        """

        SELECT LGA_ID

        FROM LGA

        WHERE LGA_NAME=?

        """,

        (lga,)

    ).fetchone()

    if result:

        lga_id = result[0]

    else:

        lga_id = None

    minx, miny, maxx, maxy = row.geometry.bounds

    cursor.execute(

        """

        INSERT INTO Ward

        (

        WardName,

        LGA_ID,

        Geometry,

        MinX,

        MinY,

        MaxX,

        MaxY

        )

        VALUES

        (?,?,?,?,?,?,?)

        """,

        (

            row[ward_field],

            lga_id,

            row.geometry.wkt,

            minx,

            miny,

            maxx,

            maxy

        )

    )

# ==========================================================
# FACILITIES
# ==========================================================

cursor.execute("""

CREATE TABLE Facility(

FacilityID INTEGER PRIMARY KEY,

FacilityName TEXT,

LGA_ID INTEGER,

Longitude REAL,

Latitude REAL,

FOREIGN KEY(LGA_ID)

REFERENCES LGA(LGA_ID)

)

""")

name_field = detect(

    facilities.columns,

    ["facility", "name"]

)

for _, row in facilities.iterrows():

    result = cursor.execute(

        """

        SELECT LGA_ID

        FROM LGA

        WHERE LGA_NAME=?

        """,

        (row[facility_lga],)

    ).fetchone()

    if result:

        lga_id = result[0]

    else:

        lga_id = None

    cursor.execute(

        """

        INSERT INTO Facility

        (

        FacilityName,

        LGA_ID,

        Longitude,

        Latitude

        )

        VALUES

        (?,?,?,?)

        """,

        (

            row[name_field],

            lga_id,

            row[lon_field],

            row[lat_field]

        )

    )

# ==========================================================
# INDEXES
# ==========================================================

cursor.execute(

"CREATE INDEX idx_facility_lga ON Facility(LGA_ID)"

)

cursor.execute(

"CREATE INDEX idx_ward_lga ON Ward(LGA_ID)"

)

cursor.execute(

"CREATE INDEX idx_lga_senatorial ON LGA(SenatorialID)"

)

cursor.execute(

"CREATE INDEX idx_ward_bbox ON Ward(MinX,MinY,MaxX,MaxY)"

)

conn.commit()

conn.close()

logger.success("Spatial database created.")

print("\n====================================")
print("QUESTION 2.2 COMPLETED")
print("====================================")
print(f"Database : {DATABASE}")
print("Primary Keys      : YES")
print("Foreign Keys      : YES")
print("Indexes           : YES")
print(f"Declared CRS      : {crs}")
print("====================================")