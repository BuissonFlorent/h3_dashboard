import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from dash import html
import plotly.graph_objects as go

# For now, we will just test the layout structure directly
# Later, we can use Selenium for integration tests

def get_map_visualization_component():
    from components.map_visualization import get_map_visualization_component
    return get_map_visualization_component()

def test_map_visualization_component_loads():
    map_visualization_component = get_map_visualization_component()
    assert isinstance(map_visualization_component, html.Div)

def test_map_visualization_component_contains_plotly_figure():
    map_visualization_component = get_map_visualization_component()
    assert any(
        isinstance(child, go.Figure) for child in map_visualization_component.children
    ), "Map visualization component missing Plotly figure"

def test_map_visualization_component_updates_when_data_changes():
    # This test will be implemented later when data updates are integrated
    pass

def test_map_visualization_component_handles_errors_gracefully():
    # This test will be implemented later when error handling is integrated
    pass 