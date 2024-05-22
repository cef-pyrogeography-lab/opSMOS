#Given a geopandas object gpd of type multipolygon , I want to create a dataframe df with columns x, y, L1, L2, L3, where each row is a vertex, L1 is the ring index, L2 is the part index and L3 is the feature index

import geopandas as gpd
import pandas as pd

def extract_vertices(geodf):
    data = []
    for feature_index, geom in enumerate(geodf.geometry):
        if geom.type == 'MultiPolygon':
            for part_index, poly in enumerate(geom):
                # Exterior ring
                exterior_coords = poly.exterior.coords
                for ring_index, (x, y) in enumerate(exterior_coords):
                    data.append([x, y, 0, part_index, feature_index])
                
                # Interior rings
                for interior_index, interior in enumerate(poly.interiors):
                    interior_coords = interior.coords
                    for ring_index, (x, y) in enumerate(interior_coords):
                        data.append([x, y, interior_index + 1, part_index, feature_index])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=['x', 'y', 'L1', 'L2', 'L3'])
    return df

# Example usage
# Assuming `gdf` is your GeoDataFrame containing MultiPolygons
df = extract_vertices(gdf)
print(df)
