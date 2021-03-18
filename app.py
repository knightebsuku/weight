import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from datetime import date
import psycopg2
import os

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

db_connection = os.environ["DATABASE_URL"]
conn = psycopg2.connect(db_connection)


df = pd.read_sql("SELECT date, kg FROM weight", conn)
# df = pd.read_csv("weight.csv")
# df = df.iloc[::-1]

fig = px.scatter(df, x="date", y="kg")


app.layout = html.Div(
    children=[
        html.H1("Weight"),
        html.Div("Tracking Weight over time"),
        html.Div(
            children=[
                html.Label("Weight"),
                dcc.Input(id="weight", value="", type="number"),
            ]
        ),
        html.Div(
            children=[
                html.Label("date"),
                dcc.DatePickerSingle(
                    id="weight_date",
                    min_date_allowed=date(2021, 1, 1),
                    max_date_allowed=date(2025, 1, 1),
                    initial_visible_month=date(2021, 3, 1),
                    display_format="YYYY-MM-DD",
                    date=date.today(),
                ),
            ]
        ),
        html.Div(id="error-state"),
        html.Button(id="submit-button-state", n_clicks=0, children="Submit"),
        dcc.Graph(id="graph", figure=fig),
        html.Div(
            children=[
                dash_table.DataTable(
                    id="table",
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict("records"),
                )
            ]
        ),
    ]
)


@app.callback(
    Output("error-state", "children"),
    Output("graph", "figure"),
    Output("table", "data"),
    Input("submit-button-state", "n_clicks"),
    State("weight", "value"),
    State("weight_date", "date"),
)
def update_weight(n_clicks, weight, dates):
    """
    Update weight graph and add value to table
    """
    if weight == "" or date == "":
        return "Fill in weight and date", fig, df.to_dict("records")
    if weight > 120 or weight < 50:
        return "Weight value is incorrect", fig, df.to_dict("records")

    try:
        date.fromisoformat(dates)
    except ValueError:
        return "incorrect date format", fig, df.to_dict("records")

    cur = conn.cursor()
    cur.execute("INSERT INTO weight(date, kg) VALUES(%s,%s)", (dates, weight))
    conn.commit()
    updated_df = pd.read_sql("SELECT date, kg FROM weight", conn)
    return ("", px.scatter(updated_df, x="date", y="kg"), updated_df.to_dict("records"))


if __name__ == "__main__":
    app.run_server(debug=True, port=8080, host="0.0.0.0")
