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
        dcc.Store(id="live_hv_dose_data", storage_type="session"),
        dcc.Store(id="live_pressure_data", storage_type="session"),
        dcc.Store(id="live_refDet_data", storage_type="session"),
        dcc.Store(id="live_d2flow_data", storage_type="session"),
        dcc.Store(id="live_mw_data", storage_type="session"),
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
                                                )
                                            ],
                                            className="table__1",
                                            ),
                        ],
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