import re, os, random, datetime as dt

import dash_bootstrap_components as dbc
import dash
from dash import html, dcc
from dash.dash_table import DataTable
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import plotly.graph_objs as go, plotly.express as px, pandas as pd, numpy as np, sqlalchemy as sql

def empty_fig():
    fig = go.Figure()
    return fig

app = dash.Dash(__name__, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=4, minimum-scale=0.5,'},],
external_stylesheets=["static/boostrap.min.css"])
server = app.server

years = [str(x) for x in range(1999, 2020, 1)]
pie_parser = {"mode": {0: "minor", 1: "major"}, "key": {0:"C", 1:"C# / D-flat", 2:"D", 3:"D# / E-flat", 4:"E", 5:"F", 6:"F# / G-flat", 7: "G", 8:"G# / A-flat", 9:"A", 10:"A# / B-flat", 11:"B"},
"timesignature": {3: "3/4", 4: "4/4", 5: "5/4", 1: "4/4", 0: "4/4", np.nan: "4/4"}}


engine = sql.create_engine("sqlite:///./data/music.db")
with engine.connect() as con:
    billboard = pd.read_sql("SELECT * FROM billboard", con=con, parse_dates="WeekID")
    attributes = pd.read_sql("SELECT * FROM attributes", con=con, parse_dates="release_date").dropna(thresh=14)
    artists = pd.read_sql("SELECT * FROM artists", con=con)
    recommend_join = pd.read_sql("SELECT * FROM recommendation_join", con=con)
    artists_join = pd.read_sql("SELECT * FROM artists_join", con=con)


attributes.loc[attributes['timesignature'].isna(), 'timesignature'] = 1
attributes.loc[:, "explicit"] = attributes.explicit.apply(lambda x: "explicit" if x == 1 else "clean")
attributes.loc[:, "timesignature"] = attributes.timesignature.apply(lambda x: pie_parser["timesignature"][x])
attributes.loc[:, "key"] = attributes.key.apply(lambda x: pie_parser["key"][x])
attributes.loc[:, "mode"] = attributes["mode"].apply(lambda x: pie_parser["mode"][x])
attributes.loc[:, "genre_super"] = attributes.genre_super.apply(lambda x: "other" if x == "missing" or x == "empty" else x)
dash_data = billboard.merge(attributes, "left", on="SongID").drop_duplicates("SongID").assign(count = 1).dropna()
noncharters_data = attributes[lambda x: x.chart == 0.0].assign(count = 1)



sample_artists = attributes.merge(artists.merge(artists_join, "left", on=["artist_id"]), "left", left_on="id_y", right_on="song_id").drop_duplicates(["artist", "song_id"]).drop_duplicates(["artist_id"])
dash_data = dash_data.rename(columns={"bill_popularity_y": "Chart Points"})
dash_artists = billboard.merge(attributes, "left", on="SongID").merge(artists.merge(artists_join, "left", on=["artist_id"]), "left", left_on="id_y", right_on="song_id").drop_duplicates(["artist", "song_id"]).drop_duplicates(["artist_id"])
dash_artists.loc[:, "popularity_y"] = dash_artists.loc[:, "popularity_y"].astype("float")

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
                dbc.Label("Year Selector: "),
                dcc.Slider(id="year_slider", min=int(years[0]), max=int(years[-1]), step=1, included=False, value=1999, marks={y: y for y in years}),
            ], lg=10, md=12),
            dbc.Col(lg=1),
            dbc.Col(lg=1),
            dbc.Col([
                html.H1("Spotify Categorical Attributes"),
                html.Br(),
                dcc.Graph(figure=empty_fig(), id="explicit_pie"),
                dcc.Graph(figure=empty_fig(), id="timesig_pie"),
                dcc.Graph(figure=empty_fig(), id="key_pie"),
                dcc.Graph(figure=empty_fig(), id="genreSuper_pie"),
                dcc.Graph(figure=empty_fig(), id="mode_pie")
                ], lg=10, style={"textAlign": "center"}),
            dbc.Col(lg=1),
            dbc.Col(lg=1),
            dbc.Col([
                html.H1("Spotify Interval Attributes Distribution"),
                html.Br(),
                dcc.Graph(figure=empty_fig(), id="dance_hist"),
                dcc.Graph(figure=empty_fig(), id="energy_hist"),
                dcc.Graph(figure=empty_fig(), id="valence_hist"),
                dcc.Graph(figure=empty_fig(), id="liveness_hist"),
                dcc.Graph(figure=empty_fig(), id="speechiness_hist"),
                dcc.Graph(figure=empty_fig(), id="acousticness_hist"),
                dcc.Graph(figure=empty_fig(), id="instrumentalness_hist"),
                dcc.Graph(figure=empty_fig(), id="duration_hist"),
                dcc.Graph(figure=empty_fig(), id="loudness_hist"),
                dcc.Graph(figure=empty_fig(), id="tempo_hist"),
            ], lg=10, style={"textAlign": "center"}),
            dbc.Col(lg=1),
            dbc.Col(lg=1),
            dbc.Col([
                html.H1("Popularity Then and Now"),
                html.Br(),
                dcc.Graph(figure=empty_fig(), id="spot_pop_hist"),
                dcc.Graph(figure=empty_fig(), id="chart_pop_hist"),
                dcc.Graph(figure=empty_fig(), id="scaled_pop_hist"),
                dcc.Graph(figure=empty_fig(), id="artist_pop_hist"),
                dcc.Graph(figure=empty_fig(), id="followers"),
                ], lg=10, style={"textAlign": "center"}),
            dbc.Col(lg=1),
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

@app.callback(
    Output('explicit_pie', 'figure'),
    Output('timesig_pie', 'figure'),
    Output('key_pie', 'figure'),
    Output('genreSuper_pie', 'figure'),
    Output('mode_pie', 'figure'),
    Input('year_slider', 'value')
    )
def update_pies(year):
    if not year:
        raise PreventUpdate
    segment_data = dash_data[lambda x: (x.WeekID >= dt.datetime(year, 1, 1)) &( x.WeekID <= dt.datetime(year, 12, 31))]
    sample_data = noncharters_data[lambda x: (x.release_date >= dt.datetime(year, 1, 1)) &(x.release_date <= dt.datetime(year, 12, 31))]
    categorical_columns = {"explicit": {"name": "Explicit", "cmap": {'clean': "#00CC96", "explicit": "#FD3216"}},
    "timesignature": {"name": "Time Signatures", "cmap": {"4/4": "#EB663B", "3/4": "#AB63FA", "5/4": "#BCBD22"}},
    "key": {"name": "Pitch Class", "cmap": {"C": "#B10DA1", "C# / D-flat": "#1CFFCE", "D": "#F6222E", "D# / E-flat":"#90AD1C", "E": "#F8A19F", "F": "#FEAF16", "F# / G-flat": "#F7E1A0", "G": "#AA0DFE", "G# / A-flat": "#782AB6", "A": "#FA0087", "A# / B-flat": "#1616A7", "B": "#778AAE"}},
    "genre_super": {"name": "Major Genre", "cmap": {'r&b': "#6A76FC", 'pop': "#FE00CC", 'country': "#FF9616", 'indie': "#F6F926", 'rock': "#479B55", 'rap': "#FD3216", 'other': "#EEA6FB",
       'christian': "#DC587D", 'metal': "#6E899C", 'electronic': "#22FFA7", 'latin': "#B68E00", 'soundtrack': "#1616A7", 'jazz': "#222A2A",
       'reggae': "#7F7F7F"}},
    "mode": {"name": "Modality", "cmap": {"major": "#19D3F3", "minor": "#FF6692"}}}
    figs = []
    for category in categorical_columns.keys():
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
        fig.add_trace(go.Pie(values=segment_data.groupby(category).count().sort_index().reset_index().year.values, labels=list(segment_data.groupby(category).count().sort_index().index), hole=.4, marker_colors=[categorical_columns[category]["cmap"][l] for l in segment_data.groupby(category).count().sort_index().index]), 1, 1)
        fig.add_trace(go.Pie(values=sample_data.groupby(category).count().sort_index().reset_index().Song.values, labels=list(sample_data.groupby(category).count().sort_index().index), hole=.4), 1, 2)
        fig.update_layout(title_text=f"{category} % in {year}", template="plotly_dark",
        annotations=[dict(text='Hot 100', x=0.198, y=0.5, font_size=15, showarrow=False),
                 dict(text="Non-Charters", x=0.815, y=0.5, font_size=15, showarrow=False)])
        fig.update_traces(hoverinfo="label+percent+name")
        figs.append(fig)
        # .update_layout(template="plotly_dark", uniformtext_minsize=12, uniformtext_mode='hide') , color=category, color_discrete_map=categorical_columns[category]['cmap'],

    return figs[0], figs[1], figs[2], figs[3], figs[4]


@app.callback(
    Output('dance_hist', 'figure'),
    Output('energy_hist', 'figure'),
    Output('valence_hist', 'figure'),
    Output('liveness_hist', 'figure'),
    Output('speechiness_hist', 'figure'),
    Output('acousticness_hist', 'figure'),
    Output('instrumentalness_hist', 'figure'),
    Output('duration_hist', 'figure'),
    Output('loudness_hist', 'figure'),
    Output('tempo_hist', 'figure'),
    Output('spot_pop_hist', 'figure'),
    Output('chart_pop_hist', 'figure'),
    Output('scaled_pop_hist', 'figure'),
    Output('artist_pop_hist', 'figure'),
    Output('followers', 'figure'),
    Input('year_slider', 'value'))
def update_hists(year):
    if not year:
        raise PreventUpdate
    columns = ["chart", "danceability", "energy", "valence", "liveness", "speechiness", "acousticness", "instrumentalness", "duration", "loudness", "tempo","popularity"]
    segment_data = dash_data[lambda x: (x.WeekID >= dt.datetime(year, 1, 1)) &( x.WeekID <= dt.datetime(year, 12, 31))]
    avg_data = dash_data[lambda x: ~((x.WeekID >= dt.datetime(year, 1, 1)) &( x.WeekID <= dt.datetime(year, 12, 31)))].sample(n=segment_data.shape[0])

    segment_data_a = sample_artists[lambda x: (x.release_date >= dt.datetime(year, 1, 1)) & (x.release_date <= dt.datetime(year, 12, 31))]    
    segment_data_b = dash_artists[lambda x: (x.WeekID >= dt.datetime(year, 1, 1)) &( x.WeekID <= dt.datetime(year, 12, 31))]
    segment_data_c = pd.concat([segment_data_b.loc[:, ["followers", "popularity_y", "chart"]].fillna(1.0), segment_data_a.loc[:, ["followers", "popularity_y", "chart"]]], axis=0, ignore_index=True)

    segment_other = noncharters_data[lambda x: (x.release_date >= dt.datetime(year, 1, 1)) & (x.release_date <= dt.datetime(year, 12, 31))]
    full_segment = pd.concat([segment_other.loc[:, columns], segment_data.loc[:, columns]], axis=0, ignore_index=True)
    averages_of_charters = pd.concat([segment_data.assign(chart_year = lambda x: 1.0), avg_data.assign(chart_year = lambda x: 0.0)], axis=0, ignore_index=True)



    figs = []
    figs.append([px.histogram(full_segment, x=h, color="chart").update_layout(template="plotly_dark") for h in columns if h!="chart"])


    figs[0].append(px.histogram(averages_of_charters, x="Chart Points", color="chart_year").update_layout(template="plotly_dark"))
    figs[0].append(px.histogram(averages_of_charters, x="scaled_popularity", color="chart_year").update_layout(template="plotly_dark"))
    figs[0].append(px.histogram(segment_data_c, x="popularity_y", color="chart").update_layout(template="plotly_dark"))
    figs[0].append(px.histogram(segment_data_c, x="followers", color="chart").update_layout(template="plotly_dark"))
    return figs[0][0], figs[0][1], figs[0][2], figs[0][3], figs[0][4], figs[0][5], figs[0][6], figs[0][7], figs[0][8], figs[0][9], figs[0][10], figs[0][11], figs[0][12], figs[0][13], figs[0][14]







if __name__ == '__main__':
    app.run_server(debug=True)

