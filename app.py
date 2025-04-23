import boundary_to_hexmap as bth

# --- Configuration ---
H3_RESOLUTION = 8
OUTPUT_FILE = "chicago_h3_random.html"
CSV_FILE = "City_Boundary_20250423.csv"
HEX_ID_FILE = "chicago_hex_ids.txt"

def main():
    """
    Main function to generate Chicago hexagon map and save hexagon IDs.
    """
    # Process the boundary file and generate a map
    hexagons = bth.boundary_to_hexmap(
        csv_file=CSV_FILE,
        resolution=H3_RESOLUTION,
        hex_output_file=HEX_ID_FILE,
        map_output_file=OUTPUT_FILE
    )
    
    print(f"Process completed successfully with {len(hexagons)} hexagons.")

if __name__ == "__main__":
    main() 