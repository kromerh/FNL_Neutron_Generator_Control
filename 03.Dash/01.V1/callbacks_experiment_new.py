import pymysql
import sqlalchemy as sql

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app

# new experiment text message display that data was saved to db
@app.callback(
    Output("new-experiment-modal", "is_open"),
    [Input("new-experiment-btn-save", "n_clicks"), Input("new-experiment-modal-btn-close", "n_clicks")],
    [State("new-experiment-modal", "is_open")],
)
def toggle_modal_new_experiment(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

