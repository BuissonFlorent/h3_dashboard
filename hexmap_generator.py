import pandas as pd
import numpy as np
import boundary_to_hexmap as bth

def load_hex_ids(hex_file):
    """
    Load hexagon IDs from a file.
    
    Args:
        hex_file: Path to file containing hexagon IDs (one per line)
        
    Returns:
        Set of hexagon IDs
    """
    return bth.load_hexagons_from_file(hex_file)

def generate_map_from_hexagons(hexagons, values=None, value_column=None, 
                              title=None, output_file="hexagon_map.html", 
                              center_lat=None, center_lon=None, colorscale="Viridis"):
    """
    Generate a map from a set of hexagons and optional values.
    
    Args:
        hexagons: Set of H3 hexagon IDs
        values: DataFrame with h3_index and value columns (optional)
        value_column: Column name in DataFrame to use for coloring
        title: Map title
        output_file: Path to save the HTML output
        center_lat: Center latitude for the map (optional)
        center_lon: Center longitude for the map (optional)
        colorscale: Color scale for the map
        
    Returns:
        True if successful, False otherwise
    """
    if not hexagons:
        print("No hexagons provided")
        return False
    
    print(f"Generating map with {len(hexagons)} hexagons")
    
    # If no values provided, create random values
    if values is None:
        df = bth.create_hexagon_dataframe(hexagons, with_random_values=True)
        value_column = 'random_value'
    else:
        df = values
        if value_column is None:
            print("No value column specified, using first non-h3_index column")
            value_columns = [col for col in df.columns if col != 'h3_index']
            if value_columns:
                value_column = value_columns[0]
            else:
                print("No value columns found, adding random values")
                df['random_value'] = np.random.rand(len(df))
                value_column = 'random_value'
    
    # Create the map
    fig = bth.create_hexagon_map(
        hexagons=hexagons,
        values=df,
        value_column=value_column,
        title=title or f"Hexagon Map with {value_column}",
        center_lat=center_lat,
        center_lon=center_lon,
        colorscale=colorscale
    )
    
    # Save the map
    success = bth.save_map_to_html(fig, output_file)
    return success

def map_from_hexfile(hex_file, value_file=None, value_column=None, 
                    output_file="hexagon_map.html", title=None,
                    center_lat=None, center_lon=None, colorscale="Viridis"):
    """
    Create a map from a file of hexagon IDs and optional value file.
    
    Args:
        hex_file: Path to file containing hexagon IDs (one per line)
        value_file: Path to CSV file with h3_index and value columns (optional)
        value_column: Column name in value file to use for coloring
        output_file: Path to save the HTML output
        title: Map title
        center_lat: Center latitude for the map (optional)
        center_lon: Center longitude for the map (optional)
        colorscale: Color scale for the map
        
    Returns:
        True if successful, False otherwise
    """
    # Load hexagons
    hexagons = load_hex_ids(hex_file)
    if not hexagons:
        print(f"No hexagons found in {hex_file}")
        return False
    
    # Load values if provided
    values = None
    if value_file:
        try:
            values = pd.read_csv(value_file)
            if 'h3_index' not in values.columns:
                print("Warning: value file does not contain 'h3_index' column")
                # Try to find a column that could be the h3_index
                for col in values.columns:
                    if values[col].dtype == 'object' and values[col].str.startswith('8').any():
                        print(f"Using column '{col}' as h3_index")
                        values = values.rename(columns={col: 'h3_index'})
                        break
        except Exception as e:
            print(f"Error loading value file {value_file}: {e}")
            values = None
    
    # Generate the map
    return generate_map_from_hexagons(
        hexagons=hexagons,
        values=values,
        value_column=value_column,
        title=title,
        output_file=output_file,
        center_lat=center_lat,
        center_lon=center_lon,
        colorscale=colorscale
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a map from a list of hexagons")
    parser.add_argument("hex_file", help="File containing hexagon IDs (one per line)")
    parser.add_argument("--value-file", help="CSV file with h3_index and value columns")
    parser.add_argument("--value-column", help="Column name in value file to use for coloring")
    parser.add_argument("--output", default="hexagon_map.html", help="Output HTML file")
    parser.add_argument("--title", help="Map title")
    parser.add_argument("--center-lat", type=float, help="Center latitude for the map")
    parser.add_argument("--center-lon", type=float, help="Center longitude for the map")
    parser.add_argument("--colorscale", default="Viridis", help="Color scale for the map")
    
    args = parser.parse_args()
    
    success = map_from_hexfile(
        hex_file=args.hex_file,
        value_file=args.value_file,
        value_column=args.value_column,
        output_file=args.output,
        title=args.title,
        center_lat=args.center_lat,
        center_lon=args.center_lon,
        colorscale=args.colorscale
    )
    
    if success:
        print(f"Map successfully created and saved to {args.output}")
    else:
        print("Failed to create map") 