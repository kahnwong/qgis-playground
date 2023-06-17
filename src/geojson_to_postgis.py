import glob
import logging
import os

import geopandas as gpd
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.setLevel(logging.INFO)

###############
# INIT
###############
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

engine = create_engine(
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_DATABASE}"
)

###############
# MAIN
###############
files = glob.glob("data/layers/*.geojson")

for i in files:
    ### read
    logger.info(f"Reading: {i}")
    df = gpd.read_file(i, driver="GeoJSONSeq")
    df = df.set_crs("epsg:4326")
    logger.info(f"\tRows: {len(df)}")

    ### write to postgis
    logger.info("\t Writing to postgis...")

    layer_name = i.split("/")[-1].split(".")[0]
    df.to_postgis(layer_name, engine, if_exists="replace")

    logger.info("\t Successfully written to postgis...")
