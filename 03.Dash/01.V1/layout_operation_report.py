import pymysql
import sqlalchemy as sql

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq

layout_operation_report = html.Div(id='sensor_readout_parent',children=
    [],
    style={"display": "flex", "flex-direction": "column"},
)