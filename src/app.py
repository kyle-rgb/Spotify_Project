import re, os

import dash_bootstrap_components as dbc
import dash
from dash import html, dcc
from dash.dash_table import DataTable
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go, plotly.express as px, pandas as pd, numpy as np, sqlalchemy as sql

app = dash.Dash(__name__, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=4, minimum-scale=0.5,'}],
external_stylesheets=[dbc.themes.DARKLY])
server = app.server

years = [str(x) for x in range(1999, 2020, 1)]


main_layout = html.Div([
    html.Div([
        dbc.NavbarSimple([
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem(year, href=year) for year in years], label="Select Year"),
            dbc.NavItem([dbc.Button(html.B('Analysis Report'), href='/analysis')]),
            dbc.NavItem([dbc.Button(html.B('Debrief'), href='/debrief')])],
        brand="Home", brand_href="/"),
        dcc.Location(id='location'),
        html.Div(id="analysis_content"),
        html.Br(),
        dbc.Row([
            dbc.Col(lg=1),
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab([
                        html.Ul([
                            html.Br(),
                            html.Li('Years Analyzed: 20', ),
                            html.Li('Analysis Coverage: Jan 1999 - Dec 2019'),
                            html.Li('Update Frequency: Weekly'),
                            html.Li('Spotify Attributes Last Pulled: Dec 6th 2021'),
                            html.Li(['Sources: ',
                                html.A('Spotify Links', href='https://www.spotify.com')
                                ])
                            ])
                        ], label="General Data"),
                    dbc.Tab([
                        html.Ul([
                            html.Br(),
                            html.Li('An Analysis of American Popular Music and Spotify\'s Internal Track Metrics'),
                            html.Li(['Github repo: ',
                                html.A("github", href="https://github.com/kyle-rgb/Spotify_Project")
                                ])
                            ])
                    ], label="Project Details")
                ])
            ])
        ])
    ])
])










app.layout = main_layout





if __name__ == '__main__':
    app.run_server(debug=True)

