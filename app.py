import geopandas as gpd
import plotly.graph_objects as go
from shapely import wkt
import h3
import pandas as pd
import numpy as np
import json # To handle GeoJSON conversion for polyfill

# --- Configuration ---
H3_RESOLUTION = 8
OUTPUT_FILE = "chicago_h3_random.html"
CSV_FILE = "City_Boundary_20250423.csv"

# --- Load Chicago Boundary ---
try:
    # Try reading directly, inferring geometry and CRS if possible
    gdf_raw = gpd.read_file(CSV_FILE, GEOM_POSSIBLE_NAMES="the_geom", CRS="EPSG:4326")
    if 'geometry' not in gdf_raw.columns or gdf_raw.geometry.isnull().all():
        raise ValueError("Geometry column not loaded correctly by read_file.")
    print("Successfully loaded CSV using gpd.read_file with hints.")
except Exception as e:
    print(f"Direct read_file failed: {e}")
    print("Attempting with explicit pandas/shapely parsing...")
    try:
        df = pd.read_csv(CSV_FILE)
        df['geometry'] = df['the_geom'].apply(wkt.loads)
        gdf_raw = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326") # Set CRS during creation
        print("Successfully loaded CSV with manual geometry parsing and CRS set.")
    except Exception as e2:
        print(f"Manual parsing also failed: {e2}")
        exit()

# --- Check/Set CRS ---
if gdf_raw.crs is None:
    print("CRS still not set, forcefully assigning WGS84 (EPSG:4326). This is unexpected.")
    gdf_raw = gdf_raw.set_crs("EPSG:4326", allow_override=True)
elif gdf_raw.crs != "EPSG:4326":
    print(f"Original CRS was {gdf_raw.crs}. Reprojecting to WGS84 (EPSG:4326)...")
    gdf_raw = gdf_raw.to_crs("EPSG:4326")
else:
    print(f"GeoDataFrame CRS is correctly set to {gdf_raw.crs}.")

# Use the first geometry (assuming it's the main city boundary)
# GeoPandas __geo_interface__ provides the GeoJSON-like structure needed by h3
chicago_geometry_geojson = gdf_raw.geometry.iloc[0].__geo_interface__
print(f"Using geometry type: {chicago_geometry_geojson['type']}")

# --- H3 Hexagon Generation ---
print(f"Generating H3 hexagons at resolution {H3_RESOLUTION}...")

# ---- MODIFICATION START ----
# Convert the GeoJSON dict to an H3Shape object first
# Use h3shape_to_cells (preferred) or polyfill (fallback)
try:
    h3_shape = h3.geo_to_h3shape(chicago_geometry_geojson)
    hexagons = h3.h3shape_to_cells(h3_shape, H3_RESOLUTION)
    print("Using h3.h3shape_to_cells.")
except AttributeError as e_shape:
    print(f"h3shape_to_cells failed ({e_shape}), trying h3.polyfill...")
    try:
        # Fallback to the original polyfill just in case
        hexagons = h3.polyfill(chicago_geometry_geojson, H3_RESOLUTION)
        print("Using h3.polyfill (fallback).")
    except AttributeError as e_polyfill:
         print(f"h3.polyfill also failed ({e_polyfill}). Cannot generate hexagons.")
         hexagons = set() # Assign empty set to avoid downstream errors
# ---- MODIFICATION END ----

print(f"Generated {len(hexagons)} hexagons.")

# --- Prepare Data for Plotly ---
h3_df = pd.DataFrame(list(hexagons), columns=['h3_index'])

# Add random data
np.random.seed(42) # for reproducibility
h3_df['random_value'] = np.random.rand(len(h3_df))

# Function to convert H3 index to GeoJSON polygon format
def h3_to_geojson_feature(h3_index):
    # Use cell_to_boundary (v4 name) instead of h3_to_geo_boundary (v3 name)
    # h3.cell_to_boundary returns list of [lat, lng], need to swap for GeoJSON [lng, lat]
    try:
        boundary_lat_lng = h3.cell_to_boundary(h3_index)
        # Convert to GeoJSON standard [lng, lat]
        boundary_lng_lat = [coord[::-1] for coord in boundary_lat_lng]
    except AttributeError:
        print("h3.cell_to_boundary not found, trying h3.h3_to_geo_boundary (fallback)...")
        try:
            # Fallback for older versions or unexpected API
            boundary_lng_lat = h3.h3_to_geo_boundary(h3_index, geo_json=True) # Already in [lng, lat] for geo_json=True
            # Note: No swap needed if geo_json=True worked
            print("Using h3.h3_to_geo_boundary (fallback).")
        except AttributeError:
             print("h3.h3_to_geo_boundary also failed. Cannot get boundary.")
             boundary_lng_lat = [] # Empty boundary on error
        except Exception as e_fallback:
             print(f"Error in fallback h3_to_geo_boundary for {h3_index}: {e_fallback}")
             boundary_lng_lat = []
    except Exception as e:
        print(f"Error getting boundary for {h3_index} using cell_to_boundary: {e}")
        boundary_lng_lat = [] # Empty boundary on error


    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [boundary_lng_lat] # GeoJSON requires list of rings
        },
        "id": h3_index # Plotly uses 'id' to match locations/z values
    }

# Create GeoJSON structure for all hexagons
geojson_features = [h3_to_geojson_feature(h3_id) for h3_id in h3_df['h3_index']]
h3_geojson = {"type": "FeatureCollection", "features": geojson_features}

# --- Create Plotly Map ---
# Calculate centroid for map centering (use raw GDF for potentially better centroid)
center_lat = gdf_raw.geometry.unary_union.centroid.y
center_lon = gdf_raw.geometry.unary_union.centroid.x

fig = go.Figure(go.Choroplethmapbox(
    geojson=h3_geojson,
    locations=h3_df['h3_index'],
    z=h3_df['random_value'],
    colorscale="Viridis", # Or choose another colorscale: Blues, Reds, etc.
    marker_opacity=0.7,
    marker_line_width=0.5,
    marker_line_color='white',
    colorbar_title="Random Value"
))

fig.update_layout(
    title_text=f'Chicago H3 Hexagons (Res {H3_RESOLUTION}) with Random Data',
    mapbox_style="carto-positron",
    mapbox_zoom=9,
    mapbox_center={"lat": center_lat, "lon": center_lon},
    margin={"r":0,"t":30,"l":0,"b":0}
)

# --- Save Output ---
fig.write_html(OUTPUT_FILE)
print(f"Map saved to {OUTPUT_FILE}") 