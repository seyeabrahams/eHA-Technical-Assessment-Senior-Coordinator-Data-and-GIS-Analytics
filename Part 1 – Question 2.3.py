import pandas as pd
import geopandas as gpd
import re

from pathlib import Path
from rapidfuzz import process
from loguru import logger

# --------------------------------------------------------
# Project Paths
# --------------------------------------------------------

ROOT = Path(
    r"C:\Users\USER\Desktop\Technical_asssessment\All Dataset"
)

OUTPUT = ROOT / "outputs"
TABLES = OUTPUT / "tables"

OUTPUT.mkdir(exist_ok=True)
TABLES.mkdir(exist_ok=True)