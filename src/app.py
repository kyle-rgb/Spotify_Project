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
pie_parser = {"mode": {0: "minor", 1: "major"}, "key": {0:"C", 1:"C# / D-flat", 2:"D", 3:"D# / E-flat", 4:"E", 5:"F", 6:"F# / G-flat", 7: "G", 8:"G# / A-flat", 9:"A", 10:"A# / B-flat", 11:"B"},
"timesignature": {3: "3/4", 4: "4/4", 5: "5/4", 1: "4/4", 0: "4/4"}}





engine = sql.create_engine("sqlite:///./data/music.db")
with engine.connect() as con:
    billboard = pd.read_sql("SELECT * FROM billboard", con=con, parse_dates="WeekID")
    attributes = pd.read_sql("SELECT * FROM attributes", con=con, parse_dates="release_date")
    artists = pd.read_sql("SELECT * FROM artists", con=con)
    recommend_join = pd.read_sql("SELECT * FROM recommendation_join", con=con)
    artists_join = pd.read_sql("SELECT * FROM artists_join", con=con)

dash_data = billboard.merge(attributes, "left", on="SongID").drop_duplicates("SongID").assign(count = 1).dropna()
dash_data.loc[:, "explicit"] = dash_data.explicit.apply(lambda x: "explicit" if x == 1 else "clean")
dash_data.loc[:, "timesignature"] = dash_data.timesignature.apply(lambda x: pie_parser["timesignature"][x])
dash_data.loc[:, "key"] = dash_data.key.apply(lambda x: pie_parser["key"][x])
dash_data.loc[:, "genre_super"] = dash_data.genre_super.apply(lambda x: "other" if x == "missing" or x == "empty" else x)
dash_data = dash_data.rename(columns={"bill_popularity_y": "Chart Points"})
dash_artists = billboard.merge(attributes, "left", on="SongID").merge(artists.merge(artists_join, "left", on=["artist_id"]), "left", left_on="id_y", right_on="song_id").drop_duplicates(["artist", "song_id"]).drop_duplicates(["artist_id"])

fig = px.pie(dash_data, values="count", names="explicit", title= "% of Billboard Songs Explicit")
fig2 = px.pie(dash_data, values="count", names="timesignature", title="Time Signatures of Billboard Songs")
fig3 = px.pie(dash_data, values="count", names="key", title="Pitch Class of Billboard Songs")
fig4 = px.pie(dash_data, values="count", names="genre_super", title="Major Genres of Billboard Songs")

hist = px.histogram(dash_data, x="danceability")
hist1 = px.histogram(dash_data, x="energy")
hist2 = px.histogram(dash_data, x="valence")
hist3 = px.histogram(dash_data, x="liveness")
hist4 = px.histogram(dash_data, x="speechiness")
hist5 = px.histogram(dash_data, x="acousticness")
hist6 = px.histogram(dash_data, x="instrumentalness")
hist7 = px.histogram(dash_data, x="duration")
hist8 = px.histogram(dash_data, x="loudness")

hist9 = px.histogram(dash_data, x="popularity")
hist10 = px.histogram(dash_data, x="Chart Points")
hist11 = px.histogram(dash_data, x="scaled_popularity")

dash_artists.loc[:, "popularity_y"] = dash_artists.loc[:, "popularity_y"].astype("float")
hist12 = px.histogram(dash_artists, x="popularity_y", title="Billboard Artist Popularity Distribution")
hist13 = px.histogram(dash_artists, x="followers", title="Billboard Artist Followers Distribution")

main_layout = html.Div([
    html.Div([
        dbc.NavbarSimple([
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem(year, href=year) for year in years], label="Select Year"),
            dbc.NavItem([dbc.Button(html.B('Analysis Report'), href='/analysis')]),
            dbc.NavItem([dbc.Button(html.B('Debrief'), href='/debrief')])],
        brand="Home", brand_href="/"),
        dcc.Location(id='location'),
        dbc.Row([
            dbc.Col(lg=1),
            dbc.Col([
                html.H1("Spotify Categorical Attributes"),
                html.Br(),
                dcc.Graph(figure=fig, id="explicit_pie"),
                dcc.Graph(figure=fig2, id="timesig_pie"),
                dcc.Graph(figure=fig3, id="key_pie"),
                dcc.Graph(figure=fig4, id="genreSuper_pie"),
                ], lg=4, style={"textAlign": "center"}),
            dbc.Col([
                html.H1("Spotify Interval Attributes Distribution"),
                html.Br(),
                dcc.Graph(figure=hist, id="dance_hist"),
                dcc.Graph(figure=hist1, id="energy_hist"),
                dcc.Graph(figure=hist2, id="valence_hist"),
                dcc.Graph(figure=hist3, id="liveness_hist"),
                dcc.Graph(figure=hist4, id="speechiness_hist"),
                dcc.Graph(figure=hist5, id="acousticness_hist"),
                dcc.Graph(figure=hist6, id="instrumentalness_hist"),
                dcc.Graph(figure=hist7, id="duration_hist"),
                dcc.Graph(figure=hist8, id="loudness_hist"),
            ], lg=7, style={"textAlign": "center"}),
            dbc.Col(lg=1),
            dbc.Col([
                html.H1("Popularity Then and Now"),
                html.Br(),
                dcc.Graph(figure=hist9, id="spot_pop_hist"),
                dcc.Graph(figure=hist12, id="artist_pop_hist"),
                dcc.Graph(figure=hist13, id="followers"),
                dcc.Graph(figure=hist10, id="chart_pop_hist"),
                dcc.Graph(figure=hist11, id="scaled_pop_hist"),
                ], lg=11, style={"textAlign": "center"})
            ],
        id="analysis_content"),
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

