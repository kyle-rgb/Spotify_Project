# Bring in Dependencies
import pandas as pd, numpy as np, datetime as dt
import pymongo, os, json
import json
import flask
from flask import url_for, jsonify
import sqlalchemy as sql
from flask_cors import CORS, cross_origin
from workdata import manipulate_data



app = flask.Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
cors = CORS(app)



# Route
@app.route("/")
def index():
    return("Success!")



# Graph Route
@app.route("/chart/api")
@cross_origin()
def get_data():
    engine = sql.create_engine("sqlite:///../../data/processed/finalData.db")
    conn = engine.connect()
    year = flask.request.args["year"]
    resultdf = pd.read_sql("SELECT * FROM billboard_normalized", con=conn)
    pivotJSON = manipulate_data(resultdf, year=year)
    return pivotJSON

@app.route("/line_chart_race")
@cross_origin()
def draw_graph():
    year = flask.request.args["year"]
    engine = sql.create_engine("sqlite:///../../data/processed/finalData.db")
    conn = engine.connect()
    radar_json = pd.read_sql(f"SELECT Top_Genre, AVG(explicit) explicit, AVG(duration) duration, AVG(danceability) danceability, AVG(energy) energy, AVG(loudness) loudness, AVG(mode) mode, AVG(speechiness) speechiness, AVG(acousticness) acousticness, AVG(valence) valence, AVG(tempo) tempo FROM (SELECT DISTINCT SongID, Top_Genre, explicit, duration, danceability, energy, loudness, mode, speechiness, acousticness, valence, tempo FROM billboard_normalized WHERE chart_Year = {year}) GROUP BY Top_Genre", con=conn).to_dict(orient="records")
    conn.close()
    return flask.render_template("jsontest.html", pyyear=year, radar_json=radar_json)

# @app.route("/test/")
# @cross_origin()
# def draw_graphz():
#     year = flask.request.args["year"]
#     engine = sql.create_engine("sqlite:///../../data/processed/finalData.db")
#     conn = engine.connect()
#     radar_json = pd.read_sql("SELECT Top_Genre, AVG(explicit) explicit, AVG(duration) duration, AVG(danceability) danceability, AVG(energy) energy, AVG(loudness) loudness, AVG(mode) mode, AVG(speechiness) speechiness, AVG(acousticness) acousticness, AVG(valence) valence, AVG(tempo) tempo, AVG(instrumentalness) instrumentalness FROM (SELECT DISTINCT SongID, Top_Genre, explicit, duration, danceability, energy, loudness, mode, speechiness, acousticness, valence, tempo, instrumentalness FROM billboard WHERE chart_Year = 2010) GROUP BY Top_Genre", con=conn).to_json(orient="records")
#     conn.close()
#     return radar_json



if __name__ == "__main__":
    app.run()
