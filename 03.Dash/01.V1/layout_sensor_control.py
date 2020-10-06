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

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
cwd = os.getcwd()
df_hostnames = pd.read_csv(f'{cwd}/pi_hostnames.csv')


# Connect to the database

# read password and user to database
credentials_file = r'../../credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}

sql_engine = sql.create_engine(connect_string)

query = f"SELECT * FROM experiment_control;"
df = pd.read_sql(query, sql_engine)

# read microwave settings from database
mw_fp_set = df['mw_fp_set'].values[0]
mw_freq_set = df['mw_freq_set'].values[0]

# flow meter settings
d2flow_set = df['d2flow_set'].values[0]

layout_sensor_control = html.Div(id='sensor_control_parent',children=
    [
        dcc.Store(id="aggregate_data"),
        dcc.Store(id="d2flow_set"),
        dcc.Store(id="mw_set"),
        dcc.Store(id="mw_onoff"),
        dcc.Store(id="mw_freq_set"),
        dcc.Interval(
            id='readout_interval',
            interval=1.5*1000, # in milliseconds
            n_intervals=0
        ),
        dcc.Store(id="live_hv_dose_data"),
        dcc.Store(id="live_pressure_data"),
        dcc.Store(id="live_refDet_data"),
        dcc.Store(id="live_d2flow_data"),
        dcc.Store(id="live_mw_data"),
        dcc.Store(id="experiment_control_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output_mw_ip"), # empty to keep track of ip of mw changed
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
                                html.H4("Sensor readout and control", style={"color":'gray'}),

                            ]
                        )
                    ],
                    className="one-third column",
                    id="title",
                ),
                html.Div(
                    [
                        html.P(children="Experiment date: 2020-08-01 10:00", style={"color":'red'}, id="P_experiment_date"),
                        html.P("Experiment ID: 99", style={"color":'red'}, id="P_experiment_id"),
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
                value="sensor_control_readout_tab",
                children=[
                    dcc.Tab(
                        label="Readout",
                        value="sensor_control_readout_tab",
                        children=[
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [html.P("HV")],
                                                            style={"margin-left":"10%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("Dose")],
                                                            style={"margin-left":"12%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("Reference detector")],
                                                            style={"margin-left":"10%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("Pressure")],
                                                            style={"margin-left":"7%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("D2 flow")],
                                                            style={"margin-left":"7%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("D2 flow setpoint")],
                                                            style={"margin-left":"7%"}
                                                        ),

                                                    ],
                                                    id="info-container",
                                                    className="row container-display",
                                                ),
                                            ],
                                            id="right-column",
                                            # className="seven columns",
                                            className="twelve columns",
                                        ),
                                    ],
                                    className="row flex-display",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_HV_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                            style={"margin-left": "4%"},
                                                        ),
                                                        html.Div(
                                                            [html.P("-100.0 kV", id="HV_kV_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [html.P("1.0 mA", id="HV_mA_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_dose_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                            style={"margin-left": "2%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("1000 muSv/h", id="dose_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [html.P("5.5 E7 n/s", id="yield_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_refDet_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                            style={"margin-left": "3%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("1200 1/s", id="refDet_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_pressure_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                            style={"margin-left": "3%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("7 E-7 mbar", id="pressure_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_d2flow_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                            style={"margin-left": "3%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("1000 mV", id="d2flow_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [daq.NumericInput(id='d2flow_input',value=int(d2flow_set), max=4000, min=0, size=120,label='mV', labelPosition='right')],
                                                            className="mini_container",
                                                            style={"margin-left": "3%"}
                                                        ),
                                                        html.Div(
                                                            [html.Button('Send', id='btn_d2flow_set', n_clicks=0)],
                                                            className="mini_container",
                                                            style={"margin-left": "-0.5%"}

                                                        ),

                                                    ],
                                                    id="info-container",
                                                    className="row container-display",
                                                ),
                                            ],
                                            id="right-column",
                                            # className="seven columns",
                                            className="ten columns",
                                        ),
                                    ],
                                    className="row flex-display",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                dcc.Graph(
                                                        id="sensor_control_graph_HV",
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
                                            className="pretty_container five columns",
                                            style={"margin-left": "2%"}
                                        ),
                                        html.Div(
                                            [
                                                dcc.Graph(
                                                        id="sensor_control_graph_pressure",
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
                                            className="pretty_container five columns",
                                        ),
                                    ],
                                    className="row flex-display",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                dcc.Graph(
                                                        id="sensor_control_graph_dose",
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
                                            className="pretty_container five columns",
                                            style={"margin-left": "2%"}
                                        ),
                                        html.Div(
                                            [
                                                dcc.Graph(
                                                        id="sensor_control_graph_d2flow",
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
                                            className="pretty_container five columns",
                                        ),
                                    ],
                                    className="row flex-display",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                        [
                                                            html.Div(
                                                                    [daq.PowerButton(id="switch_mw_on_off",
                                                                        on=False,
                                                                        label='MW ON / OFF',
                                                                        labelPosition='bottom',
                                                                        color='#FF5E5E')],
                                                                    style={"margin-left": "80%", "margin-bottom": "5%"}
                                                                ),
                                                        ],
                                                        className='row container-display'
                                                     ),
                                                html.Div(
                                                        [
                                                            html.Div(
                                                                    [html.P("FP setpoint 200 W", id="mw_setpoint_FP_text")],
                                                                    style={"margin-left": "4%", "margin-top": "1%"}
                                                                ),
                                                            html.Div(
                                                                    [html.P("FP input:")],
                                                                    style={"margin-left": "21.5%", "margin-top": "1%"}
                                                                ),
                                                            html.Div(
                                                                    [daq.NumericInput(id='FP_input',value=int(mw_fp_set), max=200, min=0, size=80,label='W', labelPosition='right')],
                                                                    # style={"margin-left": "80%"}
                                                                ),
                                                        html.Div(
                                                            [html.Button('Send', id='btn_FP_set', n_clicks=0)],
                                                            style={"margin-left": "6.5%"}

                                                        ),
                                                        ],
                                                        className='row container-display',
                                                        style={"margin-bottom": "2%"}
                                                     ),
                                                html.Div(
                                                        [
                                                            html.Div(
                                                                    [html.P("Freq setpoint 0.0 MHz", id="mw_setpoint_freq_text")],
                                                                    style={"margin-left": "4%", "margin-top": "1%"}
                                                                ),
                                                            html.Div(
                                                                    [html.P("Freq input:")],
                                                                    style={"margin-left": "10%", "margin-top": "1%"}
                                                                ),
                                                            html.Div(
                                                                    [daq.NumericInput(id='freq_input',value=int(mw_freq_set), max=2500, min=2400, size=80,label='MHz', labelPosition='right')],
                                                                    # style={"margin-left": "80%"}
                                                                ),
                                                        html.Div(
                                                            [html.Button('Send', id='btn_freq_set', n_clicks=0)],
                                                            style={"margin-left": "3.5%"}

                                                        ),
                                                        ],
                                                        className='row container-display'
                                                     ),
                                                html.Div(
                                                        [
                                                            html.Div(
                                                                    [html.P("No faults", id="mw_fault_text_no", style={"color":"#39ff14"})],
                                                                    className='three columns',
                                                                    style={"margin-left": "4%"}
                                                                ),
                                                            html.Div(
                                                                    [html.P("External safety", id="mw_fault_text_0", style={"color":"#FF5E5E"})],
                                                                    className='three columns'
                                                                ),
                                                            html.Div(
                                                                    [html.P("RP limit", id="mw_fault_text_1", style={"color":"#FF5E5E"})],
                                                                    className='three columns'
                                                                ),
                                                        ],
                                                        className='row container-display',
                                                        style={"margin-top": "5%"}
                                                     ),
                                                html.Div(
                                                        [
                                                            html.Div(
                                                                    [html.P("Local mode", id="mw_fault_text_2", style={"color":"#FF5E5E"})],
                                                                    className='three columns',
                                                                    style={"margin-left": "4%"}
                                                                ),
                                                            html.Div(
                                                                    [html.P("Gateway comm", id="mw_fault_text_3", style={"color":"#FF5E5E"})],
                                                                    className='three columns'
                                                                ),
                                                            html.Div(
                                                                    [html.P("Temperature fault", id="mw_fault_text_4", style={"color":"#FF5E5E"})],
                                                                    className='three columns'
                                                                ),
                                                        ],
                                                        className='row container-display',
                                                        style={"margin-top": "5%"}
                                                     ),
                                                html.Div(
                                                        [
                                                            html.Div(
                                                                    [html.P("Internal relay", id="mw_fault_text_5", style={"color":"#FF5E5E"})],
                                                                    className='three columns',
                                                                    style={"margin-left": "4%"}
                                                                ),
                                                            html.Div(
                                                                    [html.P("fault code: 107", id="mw_fault_text_code", style={"color":"#FF5E5E"})],
                                                                    className='three columns'
                                                                ),
                                                        ],
                                                        className='row container-display',
                                                        style={"margin-top": "5%"}
                                                     ),
                                            ],
                                            className="mini_container four columns",
                                            style={"margin-left": "2%"},
                                            id="cross-filter-options",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_mw_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                            style={"margin-left": "3%"}
                                                        ),
                                                        html.Div(
                                                            [html.P("FP: 200 W", id="FP_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [html.P("RP: 10 W", id="RP_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [html.P("f: 2445.6 MHz", id="freq_text")],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [html.P("Leak sensors:",)],
                                                            className="mini_container",
                                                            style={"margin-left": "5%"}
                                                        ),
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_leak1_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container"
                                                        ),
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_leak2_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                        ),
                                                        html.Div(
                                                            [daq.Indicator(
                                                                    id='idc_leak3_sensor',
                                                                    color="#39ff14",
                                                                    size=30,
                                                                    value=True
                                                                )],
                                                            className="mini_container",
                                                        ),
                                                    ],
                                                    id="info-container",
                                                    className="row container-display",
                                                ),
                                                html.Div(
                                                    [dcc.Graph(
                                                        id="sensor_control_graph_mw_power",
                                                        figure={
                                                            "data": [
                                                                {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                            ],
                                                            "layout": {
                                                                "height": 150,  # px
                                                                "margin": dict(t=10, b=15, l=50, r=50)
                                                            },
                                                        },
                                                    ),
                                                    dcc.Graph(
                                                        id="sensor_control_graph_mw_freq",
                                                        figure={
                                                            "data": [
                                                                {"x": [1, 2, 3], "y": [4, 1, 2], "type": "scatter"},
                                                                {"x": [1, 2, 3], "y": [2, 4, 5], "type": "scatter"},
                                                            ],
                                                            "layout": {
                                                                "height": 150,  # px
                                                                "margin": dict(t=10, b=15, l=50, r=50)
                                                            },
                                                        },
                                                    )],
                                                    id="countGraphContainer",
                                                    className="pretty_container",
                                                ),
                                            ],
                                            id="right-column",
                                            # className="seven columns",
                                            className="six columns",
                                        ),
                                    ],
                                    className="row flex-display",
                                ),
                            ],
                        ),
                    dcc.Tab(
                        label="Control",
                        value="sensor_control_control_tab",
                        children=[
                                html.Div(
                                        [# row1
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [

                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.H6("Experiment settings")],
                                                                                style={"margin-left": "4%", "margin-top": "1%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("Experiment ID:")],
                                                                                style={"margin-left": "4%", "margin-top": "1%"}
                                                                            ),
                                                                        dcc.Dropdown(
                                                                            id="sensor_control_dropdown_ID",
                                                                            options=[
                                                                                {'label': 'id1', 'value': '1'},
                                                                                {'label': 'id2', 'value': '2'},
                                                                                {'label': 'id3', 'value': '3'}
                                                                            ],
                                                                            multi=False,
                                                                            className="reag__select",
                                                                            style={"margin-left": "3%", "width": "120px"}
                                                                        ),
                                                                        html.Div(
                                                                                [html.Button('Load current', id='btn_experiment_control_read_control', n_clicks=0)],
                                                                                style={"margin-left": "6.5%"}
                                                                            ),

                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                [
                                                                    dash_table.DataTable(
                                                                        id="experiment_id_table_sensor_control",
                                                                        columns=[{"name": i, "id": i} for i in df.columns],
                                                                        data=df.to_dict('records'),
                                                                        style_cell={
                                                                            "minWidth": "0px",
                                                                            "maxWidth": "180px",
                                                                            "whiteSpace": "normal",
                                                                        },
                                                                    )
                                                                ],
                                                                className="table__1",
                                                            ),

                                                        ],
                                                        className="mini_container five columns",
                                                        style={"margin-left": "2%"},
                                                        id="cross-filter-options",
                                                    ),
                                                    html.Div(
                                                        [

                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.H6("Microwave settings")],
                                                                                style={"margin-left": "4%", "margin-top": "1%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("IP address:")],
                                                                                style={"margin-left": "4%", "margin-top": "1%"}
                                                                            ),
                                                                        dcc.Input(
                                                                            id="sensor_control_mw_ip_input",
                                                                            value="255.255.255.255",
                                                                            style={"margin-left": "3%", "width": "180px"}
                                                                        ),
                                                                        html.Div(
                                                                                [html.Button('Send', id='btn_experiment_control_mw_ip', n_clicks=0)],
                                                                                style={"margin-left": "6.5%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),

                                                        ],
                                                        className="mini_container five columns",
                                                        style={"margin-left": "2%"},
                                                        id="cross-filter-options",
                                                    ),

                                    ],
                                    className="row flex-display",
                                ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [

                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.H6("Sensor settings")],
                                                                                style={"margin-left": "4%", "margin-top": "1%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                [
                                                                    dash_table.DataTable(
                                                                        id="entry-table",
                                                                        columns=[{"name": i, "id": i} for i in df_hostnames.columns],
                                                                        data=df_hostnames.to_dict('records'),
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
                                                                        style_as_list_view=True,
                                                                    )
                                                                ],
                                                                className="table__1",
                                                                style={'margin-bottom': "5%"}
                                                            ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("HV and dose:")],
                                                                                style={"margin-left": "4%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy ssh', id='btn_copy_ssh_hv_dose', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy start control script', id='btn_copy_control_hv_dose', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("Pressure:")],
                                                                                style={"margin-left": "4%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy ssh', id='btn_copy_ssh_pressure', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy start control script', id='btn_copy_control_pressure', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("MW:")],
                                                                                style={"margin-left": "4%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy ssh', id='btn_copy_ssh_mw', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy start control script', id='btn_copy_control_mw', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy IP sniffer', id='btn_copy_find_ip_mw', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("D2flow:")],
                                                                                style={"margin-left": "4%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy ssh', id='btn_copy_ssh_d2flow', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy start control script', id='btn_copy_control_d2flow', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("Leak:")],
                                                                                style={"margin-left": "4%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy ssh', id='btn_copy_ssh_leak', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy start control script', id='btn_copy_control_leak', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),
                                                            html.Div(
                                                                    [
                                                                        html.Div(
                                                                                [html.P("Reference detectors:")],
                                                                                style={"margin-left": "4%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy ssh', id='btn_copy_ssh_refDet', n_clicks=0),
                                                                                html.Div(id='btn_copy_ssh_refDet_output')],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                        html.Div(
                                                                                [html.Button('Copy start control script', id='btn_copy_control_refDet', n_clicks=0)],
                                                                                style={"margin-left": "2.5%"}
                                                                            ),
                                                                    ],
                                                                    className='row container-display',
                                                                    style={"margin-bottom": "2%"}
                                                                 ),


                                                        ],
                                                        className="mini_container ten columns",
                                                        style={"margin-left": "2%"},
                                                        id="cross-filter-options",
                                                    ),

                                    ],
                                    className="row flex-display",
                                )

                                        ],
                                    ),
                                ],
                        ),
                    ],
                )

    ],

    style={"display": "flex", "flex-direction": "column"},
)