import pymysql
import sqlalchemy as sql

import dash
import dash_table

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
                        children=[
                                    html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            dash_table.DataTable(
                                                                id="tbl_live_overview",
                                                                style_cell={
                                                                    "minWidth": "0px",
                                                                    "maxWidth": "180px",
                                                                    "whiteSpace": "normal",
                                                                    "textAlign": "left",
                                                                    'padding': '5px',
                                                                    'font-family': 'sans-serif'
                                                                },
                                                                style_header={
                                                                    'backgroundColor': 'white',
                                                                    'fontWeight': 'bold'
                                                                },
                                                            ),
                                                        ],
                                                        className="table__1 three columns",
                                                        ),
                                                ],
                                                className="row flex-display",
                                                style = {"margin-left": "5%"},
                                            ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                            [
                                                                html.Button('Load data', id='btn_load_and_plot', n_clicks=0)
                                                            ],
                                                            className="three columns",
                                                            style = {"margin-left": "5%"},
                                                        ),
                                                ],
                                                className="row flex-display",
                                    ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_HV",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),

                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_dose",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_pressure",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_d2flow",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_mw_power",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_mw_freq",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),



                                ],
                        ),
                    dcc.Tab(
                        label="STORAGE",
                        value="tab_storage",
                        children=[
                                    html.Div(
                                                [
                                                    html.Div(
                                                            [
                                                                html.Button('Load overview', id='btn_storage_overview', n_clicks=0)
                                                            ],
                                                            className="three columns",
                                                            style = {"margin-left": "5%"},
                                                        ),
                                                ],
                                                className="row flex-display",
                                    ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            dash_table.DataTable(
                                                                id="tbl_storage_overview",
                                                                style_cell={
                                                                    "minWidth": "0px",
                                                                    "maxWidth": "360px",
                                                                    "whiteSpace": "normal",
                                                                    "textAlign": "left",
                                                                    'padding': '5px',
                                                                    'font-family': 'sans-serif'
                                                                },
                                                                style_header={
                                                                    'backgroundColor': 'white',
                                                                    'fontWeight': 'bold'
                                                                },
                                                            ),
                                                        ],
                                                        className="table__1 three columns",
                                                        ),
                                                ],
                                                className="row flex-display",
                                                style = {"margin-left": "5%", "margin-top": "1.5%"},
                                            ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                            [
                                                                dcc.Dropdown(
                                                                    id="dropdown_dates",
                                                                    options=[
                                                                        {'label': 'id1', 'value': '1'},
                                                                        {'label': 'id2', 'value': '2'},
                                                                        {'label': 'id3', 'value': '3'}
                                                                    ],
                                                                    multi=False,
                                                                    className="reag__select",
                                                                    style={"margin-left": "3%", "width": "120px"}
                                                                ),
                                                            ],
                                                            className="three columns",
                                                            style = {"margin-left": "5%"},
                                                        ),
                                                ],
                                                className="row flex-display",
                                    ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                            [
                                                                html.Button('Load data', id='btn_storage_load_and_plot', n_clicks=0)
                                                            ],
                                                            className="three columns",
                                                            style = {"margin-left": "5%"},
                                                        ),
                                                ],
                                                className="row flex-display",
                                    ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_HV_storage",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),

                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_dose_storage",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_pressure_storage",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_d2flow_storage",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_mw_power_storage",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),
                                    html.Div(
                                                [
                                                    html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                            id="graph_mw_freq_storage",
                                                                            figure={
                                                                                "data": [
                                                                                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                                                ],
                                                                                "layout": {
                                                                                    "height": 200,  # px
                                                                                    "margin": dict(t=10, b=15, l=50, r=50)
                                                                                },
                                                                            },
                                                                        ),

                                                                ],
                                                                className="pretty_container seven columns",
                                                                style={"margin-left": "2%"}
                                                        ),
                                                ],
                                            className="row flex-display"
                                        ),





                        ],
                        ),
                    ],
                ),
    ],
    style={"display": "flex", "flex-direction": "column"},
)