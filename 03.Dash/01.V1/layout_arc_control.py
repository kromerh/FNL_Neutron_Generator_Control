import pymysql
import sqlalchemy as sql
import pandas as pd
import os

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq

cwd = os.getcwd()
df_hostnames = pd.read_csv(f'{cwd}/FNL_Neutron_Generator_Control/03.Dash/01.V1//pi_hostnames.csv')

layout_arc_control = html.Div(id='motor_control_parent',children=
    [
        dcc.Store(id="motor_control_data"),
        dcc.Store(id="dump_btn"),
        dcc.Store(id="dump_btn_stop"),

        dcc.Interval(
            id='readout_interval',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ),
        html.Div(
            [
                html.Div(
                    [

                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Arc motor control", style={"color":'gray'}),

                            ]
                        )
                    ],
                    className="one-third column",
                    id="title",
                ),
                html.Div(
                    [
                        html.P(children="Experiment date: 2020-08-01 10:00", style={"color":'red'}, id="P_experiment_date"),
                        html.P("Experiment ID: -99", style={"color":'red'}, id="P_experiment_id"),
                    ],
                    className="one-third column"
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "3%"},
        ),
        dcc.Tabs(
                id="tabs",
                value="arc_motor_control_manual_tab",
                children=[
                    dcc.Tab(
                        label="Manual control",
                        value="arc_motor_control_manual_tab",
                        children=[
                                html.Div(
                                            [
                                                daq.Knob(
                                                    value=0,
                                                    id="knob_speed",
                                                    label="Speed (0 to 3200)",
                                                    labelPosition="bottom",
                                                    size=100,
                                                    color="red",
                                                    max=3200,
                                                    min=0,
                                                    style={"background": "transparent"},
                                                    className="five columns",
                                                ),
                                                daq.Knob(
                                                    value=0,
                                                    id="knob_direction",
                                                    label="Direction (negative or positive)",
                                                    labelPosition="bottom",
                                                    size=100,
                                                    color="red",
                                                    max=10,
                                                    min=-10,
                                                    className="five columns",
                                                ),
                                            ],
                                            className="row container-display",
                                        ),
                                html.Div(
                                            [

                                                daq.LEDDisplay(
                                                    id="disp_speed",
                                                    size=64,
                                                    value=0,
                                                    label="Speed",
                                                    labelPosition="bottom",
                                                    color="red",
                                                    className="five columns",
                                                ),
                                                daq.LEDDisplay(
                                                    id="disp_direction",
                                                    size=64,
                                                    value=0,
                                                    label="Direction",
                                                    labelPosition="bottom",
                                                    color="red",
                                                    className="five columns",
                                                ),
                                            ],
                                            className="row container-display",
                                        ),
                                html.Div(
                                    [html.Button('Send', id='btn_send', n_clicks=0,style={'margin-top': "2%",})],
                                    style={
                                            'textAlign':'center',
                                            'margin': 'auto'}

                                ),
                                html.Div(
                                    [html.P('<cmd>', id='P_send',style={'margin-top': "1%",})],
                                    style={
                                            'textAlign':'center',
                                            'margin': 'auto'}
                                ),
                                html.Div(
                                    [html.Button('STOP', id='btn_stop', n_clicks=0,style={'margin-top': "4%","background-color": "red"})],
                                    style={
                                            'textAlign':'center',
                                            'margin': 'auto'}

                                ),
                                html.Div(
                                        [
                                            html.Div(
                                                [
                                                    dash_table.DataTable(
                                                                id="tbl_log",
                                                                style_cell={
                                                                    "minWidth": "0px",
                                                                    "maxWidth": "180px",
                                                                    "whiteSpace": "normal",
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
                                        className="five columns"
                                ),
                            ],
                        ),
                    dcc.Tab(
                        label="Automatic control",
                        value="arc_motor_control_automatic_tab",
                        children=[
                                html.Div(),
                                ],
                        ),
                    ],
                )

    ],

    style={"display": "flex", "flex-direction": "column"},
)