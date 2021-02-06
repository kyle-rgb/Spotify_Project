# Bring in Dependencies
import pandas as pd, numpy as np, datetime as dt
import pymongo
import json
import flask
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
    resultdf = pd.read_sql("SELECT * FROM billboard", con=conn)
    print(resultdf.head())
    pivotJSON = manipulate_data(resultdf, year=year)
    return pivotJSON

@app.route("/line_chart_race")
@cross_origin()
def draw_graph():
    year = flask.request.args["year"]
    #pivotJSON = json.dumps(pivotJSON, ensure_ascii=True)
    return flask.render_template("jsontest.html", pyyear=year)

if __name__ == "__main__":
    app.run()
