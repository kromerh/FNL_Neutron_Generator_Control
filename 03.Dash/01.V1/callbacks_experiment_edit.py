import pymysql
import sqlalchemy as sql

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app



# edit experiment text message display that data was saved to db
@app.callback(
    Output("edit-experiment-modal", "is_open"),
    [Input("edit-experiment-btn-save", "n_clicks"), Input("edit-experiment-modal-btn-close", "n_clicks")],
    [State("edit-experiment-modal", "is_open")],
)
def toggle_modal_edit_experiment(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open