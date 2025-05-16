from dash import Dash, html, Input, Output, callback
from components.control_panel import get_control_panel
from components.map_visualization import get_hexmap_visualization_with_data

app = Dash(__name__)

app.layout = html.Div([
    html.H3("H3 Geospatial Dashboard - Provider Network"),
    get_control_panel(),
    html.Div(id="map-container"),
])

@callback(
    Output("map-container", "children"),
    Input("variable-dropdown", "value")
)
def update_map(selected_lob):
    return get_hexmap_visualization_with_data(selected_lob)

if __name__ == "__main__":
    app.run_server(debug=True) 