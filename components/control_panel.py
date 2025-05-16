from dash import html, dcc

def get_control_panel():
    return html.Div([
        html.H4("Line of Business"),
        dcc.Dropdown(
            id="variable-dropdown",
            options=[
                {"label": "Medicare", "value": "Medicare"},
                {"label": "Medicaid", "value": "Medicaid"}
            ],
            value="Medicare"  # Default value
        )
    ]) 