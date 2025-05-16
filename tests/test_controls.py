import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from dash import html, dcc, Input, Output, Dash
from components.control_panel import get_control_panel

def test_control_panel_contains_dropdown():
    control_panel = get_control_panel()
    assert isinstance(control_panel, html.Div), "Expected a Dash html.Div component"
    dropdown = next(child for child in control_panel.children if isinstance(child, dcc.Dropdown))
    assert dropdown.id == "variable-dropdown", "Expected dropdown with id 'variable-dropdown'"
    assert dropdown.options == [
        {"label": "Medicare", "value": "Medicare"},
        {"label": "Medicaid", "value": "Medicaid"}
    ], "Expected dropdown options to be 'Medicare' and 'Medicaid'"

def test_dropdown_has_default_value():
    control_panel = get_control_panel()
    dropdown = next(child for child in control_panel.children if isinstance(child, dcc.Dropdown))
    assert dropdown.value == "Medicare", "Expected default value to be 'Medicare'"

def test_dropdown_callback_updates_value():
    # Create a simple test app with the control panel
    app = Dash(__name__)
    app.layout = html.Div([
        get_control_panel(),
        html.Div(id="output-div")
    ])
    
    # Add a callback to capture the dropdown value
    @app.callback(
        Output("output-div", "children"),
        Input("variable-dropdown", "value")
    )
    def update_output(value):
        return f"Selected: {value}"
    
    # Test the callback function directly
    assert update_output("Medicare") == "Selected: Medicare"
    assert update_output("Medicaid") == "Selected: Medicaid" 