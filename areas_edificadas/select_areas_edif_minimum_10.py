import random
import os
from qgis.core import (QgsProject, QgsField, QgsCategorizedSymbolRenderer, 
                       QgsRendererCategory, QgsSymbol, QgsVectorLayer)
from qgis import processing
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QVariant

# --- CONFIGURATION ---
INPUT_LAYER_NAME = 'singlepart_polys'
GROUP_FIELD = 'comp_id'
MIN_COUNT = 1 # 10
# Change this path if needed
OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "Clustered_Groups.gpkg")
OUTPUT_PATH= r"C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\investigacao-projectos-reviews-alunos-juris\projetos\DGT-OpSMOS-interfaces\areas_edif_2026\clusters_edif_min_1.gpkg"

# 1. Get Input Layer
layers = QgsProject.instance().mapLayersByName(INPUT_LAYER_NAME)
if not layers:
    raise ValueError(f"Layer '{INPUT_LAYER_NAME}' not found.")
input_layer = layers[0]

# 2. Pre-calculate counts (High speed)
print("Calculating group sizes...")
counts = {}
for f in input_layer.getFeatures():
    cid = f[GROUP_FIELD]
    counts[cid] = counts.get(cid, 0) + 1

# 3. Dissolve by comp_id
print("Dissolving geometries into MultiPolygons...")
dissolve_result = processing.run("native:dissolve", {
    'INPUT': input_layer,
    'FIELD': [GROUP_FIELD],
    'OUTPUT': 'memory:Dissolved'
})
dissolved_layer = dissolve_result['OUTPUT']

# 4. Filter and Update Attributes
print(f"Filtering for groups >= {MIN_COUNT}...")
dissolved_layer.startEditing()
dissolved_layer.addAttribute(QgsField('num_features', QVariant.Int))
dissolved_layer.updateFields()

field_idx = dissolved_layer.fields().indexFromName('num_features')
ids_to_remove = []

for f in dissolved_layer.getFeatures():
    cid = f[GROUP_FIELD]
    count = counts.get(cid, 0)
    if count < MIN_COUNT:
        ids_to_remove.append(f.id())
    else:
        dissolved_layer.changeAttributeValue(f.id(), field_idx, count)

dissolved_layer.deleteFeatures(ids_to_remove)
dissolved_layer.commitChanges()

# 5. Apply Random Symbology
print("Applying random colors...")
unique_ids = sorted(list(dissolved_layer.uniqueValues(dissolved_layer.fields().indexFromName(GROUP_FIELD))))
categories = []
for val in unique_ids:
    symbol = QgsSymbol.defaultSymbol(dissolved_layer.geometryType())
    symbol.setColor(QColor.fromHsv(random.randint(0, 359), 180, 255))
    categories.append(QgsRendererCategory(str(val), symbol, str(val)))

renderer = QgsCategorizedSymbolRenderer(GROUP_FIELD, categories)
dissolved_layer.setRenderer(renderer)

# 6. Save to GeoPackage using Processing (The most stable method)
print(f"Saving to {OUTPUT_PATH}...")


processing.run("native:savefeatures", {
    'INPUT': dissolved_layer,
    'OUTPUT': OUTPUT_PATH,
    'LAYER_NAME': 'clustered_polygons'
})

# 7. Load and Embed Style
final_gpkg_layer = QgsVectorLayer(OUTPUT_PATH, "Final Clusters", "ogr")
if final_gpkg_layer.isValid():
    final_gpkg_layer.setRenderer(renderer)
    # Save style to the GeoPackage database metadata
    final_gpkg_layer.saveStyleToDatabase("Default", "Clustered by comp_id", True, "")
    QgsProject.instance().addMapLayer(final_gpkg_layer)
    print("Success! Layer saved and added to project.")