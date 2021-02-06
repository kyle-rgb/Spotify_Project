import pandas as pd, numpy as np, datetime as dt
import json

def manipulate_data(df, year):
    year =  str(year)
    df.WeekID = pd.to_datetime(df.WeekID)
    df = df[df["chart_Year"] == year]
    #df["Top_Genre"] = df["Top_Genre"].astype("str")
    translate = {"alternative": "2", "country": "5", "electronic": "9",
     "hip-hop": "4", "latin": "8", "other": "1", "pop": "6",
     "r&b": "7", "reggae": "0", "rock": "3"}
    df["Master_Genre"] = df.Top_Genre.apply(lambda x: translate[x])
    df.loc[:, ["NameJS"]] = df["Song"] + " - " + df["Performer"] + df["Master_Genre"]
    df = df.loc[:, ["WeekID", "Week_No", "SongID", "Week Position", "NameJS"]]
    data_table = df.pivot_table(index="NameJS", columns="Week_No", values="Week Position").T
    data_table = data_table.fillna(value=22)
    data_table = data_table.reset_index()
    data_table.Week_No = data_table.Week_No.astype(np.int32)
    if data_table.Week_No[0] == 0:
        data_table.Week_No = data_table.Week_No + 1
    response = data_table.to_json(orient="records")
    return response

