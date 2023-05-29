import glob
import logging
import os

from PyQt5.QtWidgets import QApplication
from qgis.core import QgsApplication
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.core import QgsVectorSimplifyMethod


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.setLevel(logging.INFO)


###############
# init
###############
# os.environ["GDAL_DATA"] = ""
os.environ["PROJ_LIB"] = "/Applications/QGIS.app/Contents/Resources/proj/"

PROJECT_NAME = "baania"
CRS = 4326

app = QApplication([])
qgs = QgsApplication([], False)

project = QgsProject.instance()
project.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(CRS))
root = project.layerTreeRoot()

###############
# main
###############
for index, layer in enumerate(glob.glob("data/layers/*.geojson")):
    slug = layer.split("/")[-1].split(".")[0]
    logger.info(f"adding layer: {slug}")

    vlayer = QgsVectorLayer(layer, slug, "ogr")

    # set simplify: https://sourcegraph.com/github.com/qgis/QGIS/-/blob/tests/src/python/test_qgsvectorlayer.py?L3316%3A15=
    simplify = QgsVectorSimplifyMethod()
    simplify.setThreshold(3)
    vlayer.setSimplifyMethod(simplify)

    # set crs
    crs = vlayer.crs()
    crs.fromEpsgId(CRS)  # WGS84
    vlayer.setCrs(crs)

    project.addMapLayer(vlayer)

    # # temp: write to file:
    # QgsVectorFileWriter.writeAsVectorFormat(
    #     vlayer, f"output/layers/{slug}.geojson", "UTF-8", vlayer.crs(), "GeoJSONSeq"
    # )

    if index == 0:
        canvas = vlayer.extent()  # init
    else:
        ext = vlayer.extent()  # to append
        canvas.combineExtentWith(ext)


###############
# WMS
# https://gis.stackexchange.com/questions/428508/qgis-server-activate-the-wmts-capabilities-wms-extent-using-pyqgis
###############
project.instance().writeEntry("WMSServiceCapabilities", "/", True)
project.instance().writeEntry("WMSServiceTitle", "/", PROJECT_NAME)
project.instance().writeEntry("WMSRootName", "/", PROJECT_NAME)
project.instance().writeEntry("WMSContactOrganization", "/", PROJECT_NAME.upper())

# WMS Capabilities: Advertised extent
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

### WMTS
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

###############
# WFS
###############
project.instance().writeEntry(
    "WFSLayers",
    "/",
    vectorLayers,
)


###############
# write
###############
project.write("./data/project.qgz")
logger.info("Succesfully write qgis project")
