import numpy as np
from scipy.spatial import KDTree
from qgis.core import QgsProject, QgsField, QgsVectorLayer, QgsGeometry
from qgis import processing
from PyQt5.QtCore import QVariant
import random

# --- CONFIGURATION ---
POINTS_LAYER_NAME = 'Vertices'
POLY_LAYER_NAME = 'Densified_Polys_3'
POINT_FIELD = 'comp_id'
NEW_POLY_FIELD = 'comp_id'

# 1. Get Layers
layers = QgsProject.instance().mapLayersByName(POLY_LAYER_NAME)
points_layers = QgsProject.instance().mapLayersByName(POINTS_LAYER_NAME)

if not layers or not points_layers:
    raise ValueError("One or both layers not found. Check the names.")

poly_layer = layers[0]
points_layer = points_layers[0]

# 2. Convert Multipart to Singlepart
print("Converting to singlepart...")
params = {'INPUT': poly_layer, 'OUTPUT': 'memory:singlepart_polys'}
result = processing.run("native:multiparttosingleparts", params)
singlepart_layer = result['OUTPUT']

# 3. Build KDTree for the 'Vertices' layer
print("Building KDTree for points...")
pt_feats = list(points_layer.getFeatures())
pt_coords = np.array([[f.geometry().asPoint().x(), f.geometry().asPoint().y()] for f in pt_feats])
pt_values = [f[POINT_FIELD] for f in pt_feats]

tree = KDTree(pt_coords)

# 4. Assign comp_id using the 1st vertex of each polygon
print("Assigning comp_id using 1st vertex...")
singlepart_layer.startEditing()

if singlepart_layer.fields().indexFromName(NEW_POLY_FIELD) == -1:
    singlepart_layer.addAttribute(QgsField(NEW_POLY_FIELD, QVariant.Int))
    singlepart_layer.updateFields()

field_idx = singlepart_layer.fields().indexFromName(NEW_POLY_FIELD)

for poly_feat in singlepart_layer.getFeatures():
    geom = poly_feat.geometry()
    if geom.isEmpty():
        continue
    
    # Get the 1st vertex of the exterior ring
    # asPolygon()[0] is the exterior ring, [0] is the first point
    first_v = geom.asPolygon()[0][0]
    
    # Nearest neighbor search in KDTree
    dist, index = tree.query([first_v.x(), first_v.y()])
    
    # Assign the comp_id
    nearest_comp_id = pt_values[index]
    singlepart_layer.changeAttributeValue(poly_feat.id(), field_idx, nearest_comp_id)

singlepart_layer.commitChanges()

# 5. Finalize
QgsProject.instance().addMapLayer(singlepart_layer)
print(f"Done! Created '{singlepart_layer.name()}' assigned by 1st vertex proximity.")


################## add symbology

LAYER_NAME = 'singlepart_polys'
ATTR_NAME = NEW_POLY_FIELD

# 1. Get the layer
layers = QgsProject.instance().mapLayersByName(LAYER_NAME)
if not layers:
    raise ValueError(f"Layer '{LAYER_NAME}' not found.")
layer = layers[0]

# 2. Get unique values from the comp_id field
unique_values = layer.uniqueValues(layer.fields().indexFromName(ATTR_NAME))

# 3. Create a list of categories
categories = []

for value in sorted(unique_values):
    # Initialize a default polygon symbol
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    
    # Generate a random RGB color
    random_color = QColor(random.randint(0, 255), 
                          random.randint(0, 255), 
                          random.randint(0, 255))
    
    symbol.setColor(random_color)
    
    # Create the category (value, symbol, label)
    category = QgsRendererCategory(str(value), symbol, str(value))
    categories.append(category)

# 4. Apply the renderer to the layer
renderer = QgsCategorizedSymbolRenderer(ATTR_NAME, categories)
layer.setRenderer(renderer)

# 5. Refresh the map
layer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(layer.id())

print(f"Applied {len(categories)} random colors to '{LAYER_NAME}'.")
