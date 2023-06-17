import glob
import logging
import os

from PyQt5.QtWidgets import QApplication
from qgis.core import QgsApplication
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsDataSourceUri
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsVectorSimplifyMethod


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.setLevel(logging.INFO)


######################
# init
######################
# os.environ["GDAL_DATA"] = ""
os.environ["PROJ_LIB"] = "/Applications/QGIS.app/Contents/Resources/proj/"

PROJECT_NAME = "baania"
CRS = 4326

app = QApplication([])
qgs = QgsApplication([], False)

project = QgsProject.instance()
project.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(CRS))
root = project.layerTreeRoot()

######################
# init ENV
######################
QGIS_BACKEND = os.getenv("QGIS_BACKEND")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

######################
# add layers
######################
for index, layer in enumerate(glob.glob("data/layers/*.geojson")):
    layer_name = layer.split("/")[-1].split(".")[0]
    logger.info(f"adding layer: {layer_name}")

    ###############
    # add layer
    ###############
    if QGIS_BACKEND == "OGR":
        vlayer = QgsVectorLayer(layer, layer_name, "ogr")

    elif QGIS_BACKEND == "POSTGIS":
        uri = QgsDataSourceUri()
        uri.setConnection(
            aUsername=DB_USERNAME,
            aPassword=DB_PASSWORD,
            aHost=DB_HOSTNAME,
            aPort=DB_PORT,
            aDatabase=DB_DATABASE,
        )
        uri.setDataSource("public", layer_name, "geometry")
        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")

    ###############
    # set simplify
    ###############
    # https://sourcegraph.com/github.com/qgis/QGIS/-/blob/tests/src/python/test_qgsvectorlayer.py?L3316%3A15=
    simplify = QgsVectorSimplifyMethod()
    simplify.setThreshold(3)
    vlayer.setSimplifyMethod(simplify)

    ###############
    # set crs
    ###############
    crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
    vlayer.setCrs(crs)
    project.addMapLayer(vlayer)

    ###############
    # set extent
    ###############
    if index == 0:
        canvas = vlayer.extent()  # init
    else:
        ext = vlayer.extent()  # to append
        canvas.combineExtentWith(ext)

######################
# WMS
######################
# https://gis.stackexchange.com/questions/428508/qgis-server-activate-the-wmts-capabilities-wms-extent-using-pyqgis
project.instance().writeEntry("WMSServiceCapabilities", "/", True)
project.instance().writeEntry("WMSServiceTitle", "/", PROJECT_NAME)
project.instance().writeEntry("WMSRootName", "/", PROJECT_NAME)
project.instance().writeEntry("WMSContactOrganization", "/", PROJECT_NAME.upper())

# WMS: Advertised extent
project.instance().writeEntry(
    "WMSExtent",
    "/",
    [
        str(canvas.xMaximum()),
        str(canvas.yMaximum()),
        str(canvas.xMinimum()),
        str(canvas.yMinimum()),
    ],
)

######################
# WMTS
######################
vectorLayers = [
    layer.id()
    for layer in project.mapLayers().values()
    if isinstance(layer, QgsVectorLayer)
]

# Project
project.instance().writeEntry("WMTSLayers", "Project", True)
project.instance().writeEntry("WMTSPngLayers", "Project", True)
project.instance().writeEntry("WMTSJpegLayers", "Project", True)

# Layers
project.instance().writeEntry("WMTSLayers", "Layer", vectorLayers)
project.instance().writeEntry("WMTSPngLayers", "Layer", vectorLayers)
project.instance().writeEntry("WMTSJpegLayers", "Layer", vectorLayers)

######################
# WFS
######################
project.instance().writeEntry(
    "WFSLayers",
    "/",
    vectorLayers,
)


######################
# write
######################
project.write("./data/project.qgz")
logger.info("Succesfully write qgis project")
