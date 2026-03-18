from qgis.core import QgsProject
from qgis import processing

# --- CONFIGURATION ---
POLY_LAYER_NAME = 'Sintra_test02_13_02_2026'
D_DENSIFY = 49.5

# 1. Get the source layer
layers = QgsProject.instance().mapLayersByName(POLY_LAYER_NAME)
if not layers:
    raise ValueError(f"Layer '{POLY_LAYER_NAME}' not found.")
poly_layer = layers[0]

# --- STEP 1: FIX GEOMETRIES ---
print("Fixing geometries...")
fix_result = processing.run("native:fixgeometries", {
    'INPUT': poly_layer, 
    'OUTPUT': 'memory:Fixed'
})

# --- STEP 2: DENSIFY ---
print(f"Densifying to {D_DENSIFY}m...")
densify_result = processing.run("native:densifygeometriesgivenaninterval", {
    'INPUT': fix_result['OUTPUT'],
    'INTERVAL': D_DENSIFY,
    'OUTPUT': 'memory:Densified_Polys_1'
})
densified_layer = densify_result['OUTPUT']

# --- STEP 2.2: DENSIFY ---
print(f"Densifying to {D_DENSIFY}m...")
densify_result = processing.run("native:densifygeometriesgivenaninterval", {
    'INPUT': fix_result['OUTPUT'],
    'INTERVAL': D_DENSIFY,
    'OUTPUT': 'memory:Densified_Polys_2'
})
densified_layer = densify_result['OUTPUT']

# --- STEP 2.3: DENSIFY ---
print(f"Densifying to {D_DENSIFY}m...")
densify_result = processing.run("native:densifygeometriesgivenaninterval", {
    'INPUT': fix_result['OUTPUT'],
    'INTERVAL': D_DENSIFY,
    'OUTPUT': 'memory:Densified_Polys_3'
})
densified_layer = densify_result['OUTPUT']

# --- STEP 3: EXTRACT VERTICES ---
# This creates a point for every single node in the polygons
print("Extracting vertices to points...")
extract_result = processing.run("native:extractvertices", {
    'INPUT': densified_layer,
    'OUTPUT': 'memory:Vertices'
})
vertices_layer = extract_result['OUTPUT']

# --- STEP 4: ADD TO PROJECT ---
QgsProject.instance().addMapLayer(densified_layer)
QgsProject.instance().addMapLayer(vertices_layer)

print("Success! Both the densified polygons and the point vertices have been added.")