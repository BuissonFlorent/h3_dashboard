from dash import html, dcc
import plotly.graph_objects as go
import hexmap_generator as hg
import boundary_to_hexmap as bth
import pandas as pd
import numpy as np
import random

def get_map_visualization_component():
    # Create a minimal Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Sample Line'))

    return html.Div([
        html.H4("Map Visualization"),
        dcc.Graph(figure=fig)
    ])

def get_hexmap_visualization():
    """
    Create a visualization of the Chicago hex map using the existing hexmap_generator code.
    """
    # Load hexagons from the existing file
    hexagons = hg.load_hex_ids("chicago_hex_ids.txt")
    
    # Create a DataFrame with random values for the hexagons
    df = bth.create_hexagon_dataframe(hexagons, with_random_values=True)
    
    # Create the map using the existing function
    fig = bth.create_hexagon_map(
        hexagons=hexagons,
        values=df,
        value_column='random_value',
        title="Chicago H3 Hexagons",
        center_lat=41.8781,  # Chicago coordinates
        center_lon=-87.6298,
        colorscale="Viridis"
    )
    
    return html.Div([
        html.H4("Chicago H3 Hexagons"),
        dcc.Graph(figure=fig)
    ])

def get_hexmap_visualization_with_data(lob):
    """
    Create a visualization of the Chicago hex map with data specific to the
    selected line of business (Medicare or Medicaid).
    
    Args:
        lob: String representing line of business ("Medicare" or "Medicaid")
    """
    # Load hexagons from the existing file
    hexagons = hg.load_hex_ids("chicago_hex_ids.txt")
    
    # Create a DataFrame with simulated data for the selected line of business
    df = create_lob_data(hexagons, lob)
    
    # Create the map using the existing function
    fig = bth.create_hexagon_map(
        hexagons=hexagons,
        values=df,
        value_column=f'{lob.lower()}_providers',
        title=f"Chicago {lob} Providers",
        center_lat=41.8781,  # Chicago coordinates
        center_lon=-87.6298,
        colorscale="Viridis" if lob == "Medicare" else "Plasma"
    )
    
    return html.Div([
        html.H4(f"Chicago {lob} Providers"),
        dcc.Graph(figure=fig)
    ])

def create_lob_data(hexagons, lob):
    """
    Create a DataFrame with simulated data for the specified line of business.
    
    Args:
        hexagons: Set of H3 hexagon IDs
        lob: String representing line of business ("Medicare" or "Medicaid")
    
    Returns:
        DataFrame with hexagon IDs and provider counts
    """
    # Start with the base hexagon dataframe
    df = bth.create_hexagon_dataframe(hexagons)
    
    # Set random seed based on LOB to ensure consistent but different data
    seed = 42 if lob == "Medicare" else 123
    random.seed(seed)
    
    # Create count data specific to the LOB
    # Medicare tends to have more providers in the north, Medicaid in the south
    if lob == "Medicare":
        # Medicare: Higher values in north (lower lat values in Chicago)
        df['medicare_providers'] = [
            int(random.betavariate(2, 5) * 50) + 5  # Between 5 and 55
            for _ in range(len(df))
        ]
    else:
        # Medicaid: Higher values in south (higher lat values in Chicago)
        df['medicaid_providers'] = [
            int(random.betavariate(3, 2) * 40) + 2  # Between 2 and 42
            for _ in range(len(df))
        ]
    
    return df 