from dash import Dash
import dash_bootstrap_components as dbc

from callbacks import register_callbacks
from layout import create_layout


app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
    ],
    suppress_callback_exceptions=True
)
server = app.server

app.layout = create_layout()
register_callbacks(app)


if __name__ == "__main__":
    app.run(port=8052, debug=False)
