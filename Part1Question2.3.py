import geopandas as gpd
import pandas as pd
import networkx as nx
import numpy as np

from pathlib import Path
from scipy.spatial import cKDTree
from shapely.geometry import Point
from loguru import logger

PROJECT = Path(
    r"C:\Users\USER\Desktop\Technical Assessment\All Dataset"
)

OUTPUT = PROJECT / "outputs"

TABLES = OUTPUT / "tables"

DATABASE = OUTPUT / "database"

roads = gpd.read_file(
    PROJECT / "road_network.geojson"
)

wards = gpd.read_file(
    PROJECT / "admin_boundaries.gpkg"
)

facilities = pd.read_csv(
    PROJECT / "health_facilities.csv"
)

staff = pd.read_csv(
    PROJECT / "minimum_staffing_norms.csv"
)

# Part B — Detect Fields Automatically

def detect(df, keywords):

    for key in keywords:

        for c in df.columns:

            if key.lower() in c.lower():

                return c

    raise ValueError(keywords)
lon = detect(
    facilities,
    ["longitude","lon","x"]
)

lat = detect(
    facilities,
    ["latitude","lat","y"]
)

ward_name = detect(
    wards,
    ["ward"]
)

population = detect(
    wards,
    ["population","pop"]
)


# Part C — Convert to GeoDataFrame

facility_gdf = gpd.GeoDataFrame(

    facilities,

    geometry=gpd.points_from_xy(

        facilities[lon],

        facilities[lat]

    ),

    crs="EPSG:4326"

)

facility_gdf = facility_gdf.to_crs(32632)

roads = roads.to_crs(32632)

wards = wards.to_crs(32632)

# Part D — Build Road Network

graph = nx.Graph()

for geom in roads.geometry:

    if geom.geom_type == "LineString":

        lines=[geom]

    elif geom.geom_type=="MultiLineString":

        lines=geom.geoms

    else:

        continue

    for line in lines:

        coords=list(line.coords)

        for i in range(len(coords)-1):

            a=coords[i]

            b=coords[i+1]

            d=Point(a).distance(Point(b))

            graph.add_edge(

                a,

                b,

                weight=d

            )

            # Part E — KDTree

            road_nodes = np.array(list(graph.nodes))

            tree = cKDTree(road_nodes)

            # Part F — Snap Facilities

            facility_nodes = []

            for p in facility_gdf.geometry:
                _, idx = tree.query([p.x, p.y])

                facility_nodes.append(

                    tuple(road_nodes[idx])

                )

            facility_gdf["road_node"] = facility_nodes

            # Part G — Snap Wards

            wards["point"] = wards.geometry.representative_point()

            ward_nodes = []

            for p in wards.point:
                _, idx = tree.query([p.x, p.y])

                ward_nodes.append(

                    tuple(road_nodes[idx])

                )

            wards["road_node"] = ward_nodes

            #  Part H — Facility Capacity

            score_field = detect(
                staff,
                ["score", "readiness", "staff"]
            )

            # Merge that score to the facility layer using the appropriate facility identifier:

            facility_id = detect(
                facilities,
                ["facility", "id", "code"]
            )

            staff_id = detect(
                staff,
                ["facility", "id", "code"]
            )

            facility_gdf = facility_gdf.merge(
                staff[[staff_id, score_field]],
                left_on=facility_id,
                right_on=staff_id,
                how="left"
            )

            facility_gdf[score_field] = facility_gdf[score_field].fillna(0)

            # Part I — Compute Accessibility Score

            scores = []

            for ward in wards.itertuples():
                # compute reachable facilities
                # sum readiness
                # divide by population

                scores.append(score)

            wards["accessibility_score"] = scores

            # Part J — Classification

            def classify(score):

                if score >= 0.75:

                    return "High"

                elif score >= 0.40:

                    return "Moderate"

                elif score > 0:

                    return "Low"

                return "None"


            wards["accessibility"] = wards[
                "accessibility_score"
            ].apply(classify)

            # Part K — Export
            wards.to_file(

                OUTPUT / "ward_accessibility.gpkg",

                driver="GPKG"

            )

            wards.drop(

                columns=["geometry", "point"],

                errors="ignore"

            ).to_csv(

                TABLES / "ward_accessibility.csv",

                index=False

            )