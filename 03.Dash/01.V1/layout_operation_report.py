import pymysql
import sqlalchemy as sql

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq

layout_operation_report = html.Div(id='operation_report_parent',children=
    [
        html.Div(
            [
                html.Div(
                    [

                    ],
                className="one-third column"
                ),
                html.Div(
                    [
                        html.H4("Operation report", style={"text-align":"center", "color":'gray'}),
                        html.Br()
                    ],
                className="one-third column"
                ),
                html.Div(
                    [

                    ],
                className="one-third column"
                ),

            ],
            className="row flex-display"
        ),
        dcc.Tabs(
                id="tabs",
                value="tab_live",
                children=[
                    dcc.Tab(
                        label="LIVE",
                        value="tab_live",
                        children=[],
                        ),
                    dcc.Tab(
                        label="STORAGE",
                        value="tab_storage",
                        children=[],
                        ),
                    ],
                ),
    ],
    style={"display": "flex", "flex-direction": "column"},
)