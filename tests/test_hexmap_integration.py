import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from dash import html
import plotly.graph_objects as go

def get_hexmap_visualization():
    from components.map_visualization import get_hexmap_visualization
    return get_hexmap_visualization()

def get_figure_from_hexmap(hexmap):
    from dash import dcc
    # Find the dcc.Graph child and return its figure
    graph = next(child for child in hexmap.children if isinstance(child, dcc.Graph))
    return graph.figure

def test_hexmap_visualization_loads():
    hexmap = get_hexmap_visualization()
    assert isinstance(hexmap, html.Div)

def test_hexmap_visualization_contains_choropleth():
    hexmap = get_hexmap_visualization()
    fig = get_figure_from_hexmap(hexmap)
    assert any(
        trace.type == 'choroplethmapbox' for trace in fig.data
    ), "Map visualization missing choropleth trace"

def test_hexmap_visualization_has_chicago_center():
    hexmap = get_hexmap_visualization()
    fig = get_figure_from_hexmap(hexmap)
    # Chicago coordinates
    assert fig.layout.mapbox.center['lat'] == pytest.approx(41.8781, abs=0.1)
    assert fig.layout.mapbox.center['lon'] == pytest.approx(-87.6298, abs=0.1)

def test_hexmap_visualization_has_hexagons():
    hexmap = get_hexmap_visualization()
    fig = get_figure_from_hexmap(hexmap)
    # Check if the choropleth has locations (hexagon IDs)
    choropleth = next(trace for trace in fig.data if trace.type == 'choroplethmapbox')
    assert len(choropleth.locations) > 0, "Map visualization has no hexagons"

def test_hexmap_visualization_returns_dash_component():
    hexmap = get_hexmap_visualization()
    assert isinstance(hexmap, html.Div), "Expected a Dash html.Div component"
    # Check that the second child is a dcc.Graph component
    from dash import dcc
    assert isinstance(hexmap.children[1], dcc.Graph), "Expected a dcc.Graph component as child" 