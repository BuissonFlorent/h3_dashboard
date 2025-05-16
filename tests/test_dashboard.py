import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from dash import Dash, html

# For now, we will just test the layout structure directly
# Later, we can use Selenium for integration tests

def get_app():
    from app_dashboard import app
    return app

def test_dashboard_loads():
    app = get_app()
    assert isinstance(app, Dash)

def test_dashboard_has_title():
    app = get_app()
    layout = app.layout
    assert any(
        hasattr(child, 'children') and 'H3' in str(child.children)
        for child in layout.children
    ), "Dashboard title missing or incorrect"

def test_dashboard_has_main_layout():
    app = get_app()
    layout = app.layout
    assert hasattr(layout, 'children'), "Main layout container missing"

def test_dashboard_has_map_container():
    app = get_app()
    layout = app.layout
    assert any(
        getattr(child, 'id', None) == 'map-container' for child in layout.children
    ), "Map container missing"

def test_dashboard_has_control_panel():
    app = get_app()
    layout = app.layout
    assert any(
        getattr(child, 'id', None) == 'control-panel' for child in layout.children
    ), "Control panel container missing" 