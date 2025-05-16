from dash import html

def get_map_component():
    return html.Div(
        id="map-container",
        style={"width": "100%", "height": "500px"}
    ) 