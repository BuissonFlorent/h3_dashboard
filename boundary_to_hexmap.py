import geopandas as gpd
import plotly.graph_objects as go
from shapely import wkt
import h3
import pandas as pd
import numpy as np
import json

def load_boundary_from_csv(csv_file):
    """
    Load a boundary from a CSV file that contains WKT geometry.
    Returns a GeoDataFrame with the boundary.
    """
    try:
        # Try reading directly, inferring geometry and CRS if possible
        gdf_raw = gpd.read_file(csv_file, GEOM_POSSIBLE_NAMES="the_geom", CRS="EPSG:4326")
        if 'geometry' not in gdf_raw.columns or gdf_raw.geometry.isnull().all():
            raise ValueError("Geometry column not loaded correctly by read_file.")
        print("Successfully loaded CSV using gpd.read_file with hints.")
    except Exception as e:
        print(f"Direct read_file failed: {e}")
        print("Attempting with explicit pandas/shapely parsing...")
        try:
            df = pd.read_csv(csv_file)
            df['geometry'] = df['the_geom'].apply(wkt.loads)
            gdf_raw = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326") # Set CRS during creation
            print("Successfully loaded CSV with manual geometry parsing and CRS set.")
        except Exception as e2:
            print(f"Manual parsing also failed: {e2}")
            raise e2

    # Check/Set CRS
    if gdf_raw.crs is None:
        print("CRS still not set, forcefully assigning WGS84 (EPSG:4326). This is unexpected.")
        gdf_raw = gdf_raw.set_crs("EPSG:4326", allow_override=True)
    elif gdf_raw.crs != "EPSG:4326":
        print(f"Original CRS was {gdf_raw.crs}. Reprojecting to WGS84 (EPSG:4326)...")
        gdf_raw = gdf_raw.to_crs("EPSG:4326")
    else:
        print(f"GeoDataFrame CRS is correctly set to {gdf_raw.crs}.")
    
    return gdf_raw

def generate_hexagons_from_boundary(gdf, resolution):
    """
    Generate H3 hexagons from a boundary GeoDataFrame at a specified resolution.
    Returns a set of H3 hexagon indexes.
    """
    # Use the first geometry (assuming it's the main boundary)
    # GeoPandas __geo_interface__ provides the GeoJSON-like structure needed by h3
    boundary_geojson = gdf.geometry.iloc[0].__geo_interface__
    print(f"Using geometry type: {boundary_geojson['type']}")

    # H3 Hexagon Generation
    print(f"Generating H3 hexagons at resolution {resolution}...")

    # Convert the GeoJSON dict to an H3Shape object first
    # Use h3shape_to_cells (preferred) or polyfill (fallback)
    try:
        h3_shape = h3.geo_to_h3shape(boundary_geojson)
        hexagons = h3.h3shape_to_cells(h3_shape, resolution)
        print("Using h3.h3shape_to_cells.")
    except AttributeError as e_shape:
        print(f"h3shape_to_cells failed ({e_shape}), trying h3.polyfill...")
        try:
            # Fallback to the original polyfill just in case
            hexagons = h3.polyfill(boundary_geojson, resolution)
            print("Using h3.polyfill (fallback).")
        except AttributeError as e_polyfill:
            print(f"h3.polyfill also failed ({e_polyfill}). Cannot generate hexagons.")
            hexagons = set()  # Assign empty set to avoid downstream errors

    print(f"Generated {len(hexagons)} hexagons.")
    return hexagons

def save_hexagons_to_file(hexagons, output_file):
    """
    Save a set of H3 hexagon indexes to a text file, one per line.
    """
    try:
        with open(output_file, 'w') as f:
            # Sort hexagons for consistent output order
            sorted_hexagons = sorted(list(hexagons))
            for hex_id in sorted_hexagons:
                f.write(f"{hex_id}\n")
        print(f"Saved {len(sorted_hexagons)} hexagon IDs to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving hexagon IDs to file: {e}")
        return False

def load_hexagons_from_file(input_file):
    """
    Load H3 hexagon indexes from a text file, one per line.
    Returns a set of H3 hexagon indexes.
    """
    try:
        with open(input_file, 'r') as f:
            hexagons = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(hexagons)} hexagon IDs from {input_file}")
        return hexagons
    except Exception as e:
        print(f"Error loading hexagon IDs from file: {e}")
        return set()

def h3_to_geojson_feature(h3_index):
    """
    Convert an H3 index to a GeoJSON feature with polygon geometry.
    """
    # Use cell_to_boundary (v4 name) instead of h3_to_geo_boundary (v3 name)
    try:
        boundary_lat_lng = h3.cell_to_boundary(h3_index)
        # Convert to GeoJSON standard [lng, lat]
        boundary_lng_lat = [coord[::-1] for coord in boundary_lat_lng]
    except AttributeError:
        print("h3.cell_to_boundary not found, trying h3.h3_to_geo_boundary (fallback)...")
        try:
            # Fallback for older versions or unexpected API
            boundary_lng_lat = h3.h3_to_geo_boundary(h3_index, geo_json=True)
            print("Using h3.h3_to_geo_boundary (fallback).")
        except AttributeError:
            print("h3.h3_to_geo_boundary also failed. Cannot get boundary.")
            boundary_lng_lat = []  # Empty boundary on error
        except Exception as e_fallback:
            print(f"Error in fallback h3_to_geo_boundary for {h3_index}: {e_fallback}")
            boundary_lng_lat = []
    except Exception as e:
        print(f"Error getting boundary for {h3_index} using cell_to_boundary: {e}")
        boundary_lng_lat = []  # Empty boundary on error

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [boundary_lng_lat]  # GeoJSON requires list of rings
        },
        "id": h3_index  # Plotly uses 'id' to match locations/z values
    }

def create_hexagon_geojson(hexagons):
    """
    Create a GeoJSON FeatureCollection from a set of H3 hexagon indexes.
    """
    geojson_features = [h3_to_geojson_feature(h3_id) for h3_id in hexagons]
    return {"type": "FeatureCollection", "features": geojson_features}

def create_hexagon_dataframe(hexagons, with_random_values=True):
    """
    Create a DataFrame from a set of H3 hexagon indexes, optionally with random values.
    """
    h3_df = pd.DataFrame(list(hexagons), columns=['h3_index'])
    
    if with_random_values:
        np.random.seed(42)  # for reproducibility
        h3_df['random_value'] = np.random.rand(len(h3_df))
    
    return h3_df

def create_hexagon_map(hexagons, values=None, value_column='value', title=None, 
                       center_lat=None, center_lon=None, colorscale="Viridis"):
    """
    Create a Plotly choropleth map from H3 hexagons and associated values.
    
    Parameters:
    - hexagons: Set or list of H3 hexagon indexes
    - values: DataFrame with h3_index and value column, or None to use random values
    - value_column: Column name in values DataFrame to use for coloring
    - title: Map title
    - center_lat, center_lon: Center coordinates for the map (optional)
    - colorscale: Color scale to use for the choropleth
    
    Returns a Plotly Figure object.
    """
    # Prepare data for Plotly
    if values is None:
        df = create_hexagon_dataframe(hexagons, with_random_values=True)
        value_column = 'random_value'
    else:
        df = values
        
    # Create GeoJSON structure for all hexagons
    h3_geojson = create_hexagon_geojson(hexagons)
    
    # Create Plotly choropleth map
    fig = go.Figure(go.Choroplethmapbox(
        geojson=h3_geojson,
        locations=df['h3_index'],
        z=df[value_column],
        colorscale=colorscale,
        marker_opacity=0.7,
        marker_line_width=0.5,
        marker_line_color='white',
        colorbar_title=value_column.replace('_', ' ').title()
    ))
    
    # Default map title if none provided
    if title is None:
        title = f'H3 Hexagon Map'
        
    # Use provided center coordinates or calculate centroid if needed
    if center_lat is None or center_lon is None:
        # Use average lat/lon from first few hexagons as a simple estimate
        try:
            # Sample up to 5 hexagons
            sample_size = min(5, len(hexagons))
            sample_hexes = list(hexagons)[:sample_size]
            
            # Get the centroids
            lats, lons = [], []
            for h3_id in sample_hexes:
                try:
                    lat, lon = h3.cell_to_center(h3_id)
                    lats.append(lat)
                    lons.append(lon)
                except AttributeError:
                    try:
                        # Fallback for older versions
                        lat, lon = h3.h3_to_geo(h3_id)
                        lats.append(lat)
                        lons.append(lon)
                    except:
                        pass
            
            if lats and lons:
                center_lat = sum(lats) / len(lats)
                center_lon = sum(lons) / len(lons)
            else:
                # Default to Chicago if everything fails
                center_lat, center_lon = 41.8781, -87.6298
        except:
            # Default to Chicago if everything fails
            center_lat, center_lon = 41.8781, -87.6298
    
    # Update layout
    fig.update_layout(
        title_text=title,
        mapbox_style="carto-positron",
        mapbox_zoom=9,
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )
    
    return fig

def save_map_to_html(fig, output_file):
    """
    Save a Plotly figure to an HTML file.
    """
    try:
        fig.write_html(output_file)
        print(f"Map saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving map to {output_file}: {e}")
        return False

def boundary_to_hexmap(csv_file, resolution, hex_output_file, map_output_file):
    """
    Main function to process a boundary file, generate hexagons, and create a map.
    """
    # Load boundary from CSV
    gdf = load_boundary_from_csv(csv_file)
    
    # Generate hexagons
    hexagons = generate_hexagons_from_boundary(gdf, resolution)
    
    # Save hexagons to file
    save_hexagons_to_file(hexagons, hex_output_file)
    
    # Calculate centroid for map centering
    center_lat = gdf.geometry.unary_union.centroid.y
    center_lon = gdf.geometry.unary_union.centroid.x
    
    # Create hexagon map with random values
    df = create_hexagon_dataframe(hexagons)
    fig = create_hexagon_map(
        hexagons, 
        values=df,
        value_column='random_value',
        title=f'Boundary H3 Hexagons (Res {resolution}) with Random Data',
        center_lat=center_lat,
        center_lon=center_lon
    )
    
    # Save map to HTML
    save_map_to_html(fig, map_output_file)
    
    return hexagons 