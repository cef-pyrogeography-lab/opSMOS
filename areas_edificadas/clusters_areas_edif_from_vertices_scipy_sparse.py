import numpy as np
from scipy.spatial import KDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from qgis.core import QgsProject, QgsField
from PyQt5.QtCore import QVariant

# --- CONFIGURATION ---
D = 50.0 
FIELD_NAME = "comp_id"
POLY_LAYER_NAME= "Vertices"

# 1. Get the source layer
layers = QgsProject.instance().mapLayersByName(POLY_LAYER_NAME)
if not layers:
    raise ValueError(f"Layer '{POLY_LAYER_NAME}' not found.")
layer = layers[0]

if not layer:
    print("No active layer found.")
else:
    # 1. Fast Coordinate Extraction
    # Using a list comprehension is faster than a standard loop
    feats = list(layer.getFeatures())
    fids = [f.id() for f in feats]
    coords = np.array([[f.geometry().asPoint().x(), f.geometry().asPoint().y()] for f in feats])

    # 2. KDTree Query
    # query_pairs is fast, but for massive datasets, we use the sparse matrix approach
    tree = KDTree(coords)
    # sparse_distance_matrix returns only points within D
    # This is much more memory efficient than query_pairs for large N
    adj_matrix = tree.sparse_distance_matrix(tree, max_distance=D+1)

    # 3. Fast Component Labeling
    # This uses a compressed sparse graph algorithm (extremely fast)
    n_components, labels = connected_components(csgraph=adj_matrix, directed=False)

    # 4. Batch Attribute Update
    layer.startEditing()
    if layer.fields().indexFromName(FIELD_NAME) == -1:
        layer.addAttribute(QgsField(FIELD_NAME, QVariant.Int))
        layer.updateFields()
    
    field_idx = layer.fields().indexFromName(FIELD_NAME)

    # Use changeAttributeValues (plural) for a batch update if possible
    # but for compatibility, we iterate the feature list once
    for i, fid in enumerate(fids):
        layer.changeAttributeValue(fid, field_idx, int(labels[i]))

    layer.commitChanges()
    print(f"Success! Processed {len(fids)} points into {n_components} components.")