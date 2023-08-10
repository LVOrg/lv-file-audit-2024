import dash_bootstrap_components as dbc
from dash import html
import dash
dash.register_page(__name__)
card = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Title", id="card-title"),
            html.H2("100", id="card-value"),
            html.P("Description", id="card-description")
        ]
    )
)

layout = html.Div([
    dbc.Row([
        dbc.Col([card]), dbc.Col([card]), dbc.Col([card]), dbc.Col([card]), dbc.Col([card])
    ]),
    dbc.Row([
        dbc.Col([card]), dbc.Col([card]), dbc.Col([card]), dbc.Col([card])
    ]),
    dbc.Row([
        dbc.Col([card]), dbc.Col([card])
    ])
])
