import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from dash import html

# For now, we will just test the layout structure directly
# Later, we can use Selenium for integration tests

def get_map_component():
    from components.map_component import get_map_component
    return get_map_component()

def test_map_component_loads():
    map_component = get_map_component()
    assert isinstance(map_component, html.Div)

def test_map_component_has_proper_sizing():
    map_component = get_map_component()
    assert map_component.style.get('width') == '100%'
    assert map_component.style.get('height') == '500px'

def test_map_component_updates_when_data_changes():
    # This test will be implemented later when data updates are integrated
    pass

def test_map_component_handles_errors_gracefully():
    # This test will be implemented later when error handling is integrated
    pass 