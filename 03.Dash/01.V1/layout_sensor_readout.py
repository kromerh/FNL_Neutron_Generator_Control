import pymysql
import sqlalchemy as sql

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq

layout_sensor_readout = html.Div(id='sensor_readout_parent',children=
    [
        dcc.Store(id="experiment_control_data_readout", storage_type="session"),
        dcc.Interval(
            id='readout_interval_readout',
            interval=5*1000, # in milliseconds
            n_intervals=0
        ),
        dcc.Store(id="live_hv_dose_data_readout", storage_type="session"),
        dcc.Store(id="live_refDet_data_readout", storage_type="session"),
        dcc.Store(id="live_pressure_data_readout", storage_type="session"),
        dcc.Store(id="live_d2flow_data_readout", storage_type="session"),
        dcc.Store(id="live_mw_data_readout", storage_type="session"),
        dcc.Store(id="live_leak_data_readout", storage_type="session"),
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
                                html.H4("Sensor readout", style={"color":'gray'}),

                            ]
                        )
                    ],
                    className="one-third column",
                    id="title",
                ),
                html.Div(
                    [
                        html.P("Experiment date: 2020-08-01 10:00", style={"color":'red'}, id="P_experiment_date_readout"),
                        html.P("Experiment ID: 99", style={"color":'red'}, id="P_experiment_id_readout"),
                    ],
                    className="one-third column"
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "3%"},
        ),
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
                                            id='idc_HV_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container",
                                    style={"margin-left": "4%"},
                                ),
                                html.Div(
                                    [html.P("-100.0 kV", id="HV_kV_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("1.0 mA", id="HV_mA_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [daq.Indicator(
                                            id='idc_dose_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container",
                                    style={"margin-left": "3%"}
                                ),
                                html.Div(
                                    [html.P("1000 muSv/h", id="dose_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("5.5 E7 n/s", id="yield_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [daq.Indicator(
                                            id='idc_refDet_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container",
                                    style={"margin-left": "3%"}
                                ),
                                html.Div(
                                    [html.P("1200 1/s", id="refDet_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [daq.Indicator(
                                            id='idc_pressure_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container",
                                    style={"margin-left": "3%"}
                                ),
                                html.Div(
                                    [html.P("7 E-7 mbar", id="pressure_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [daq.Indicator(
                                            id='idc_d2flow_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container",
                                    style={"margin-left": "3%"}
                                ),
                                html.Div(
                                    [html.P("1000 mV", id="d2flow_text_readout")],
                                    className="mini_container",
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
                                id="sensor_readout_graph_HV_readout",
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
                                id="sensor_readout_graph_pressure_readout",
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
                                id="sensor_readout_graph_dose_readout",
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
                                id="sensor_readout_graph_d2flow_readout",
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
                                            [html.P("FP setpoint 200 W", id="mw_setpoint_FP_text_readout")],
                                            style={"margin-left": "4%", "margin-top": "1%"}
                                        ),

                                ],
                                className='row container-display',
                                style={"margin-bottom": "2%"}
                             ),
                        html.Div(
                                [
                                    html.Div(
                                            [html.P("freq setpoint 2450.0 MHz", id="mw_setpoint_freq_text_readout")],
                                            style={"margin-left": "4%", "margin-top": "1%"}
                                        ),

                                ],
                                className='row container-display'
                             ),
                        html.Div(
                                [
                                    html.Div(
                                            [html.P("No faults", id="mw_fault_text_no_readout", style={"color":"#39ff14"})],
                                            className='three columns',
                                            style={"margin-left": "4%"}
                                        ),
                                    html.Div(
                                            [html.P("External safety", id="mw_fault_text_0_readout", style={"color":"#FF5E5E"})],
                                            className='three columns'
                                        ),
                                    html.Div(
                                            [html.P("RP limit", id="mw_fault_text_1_readout", style={"color":"#FF5E5E"})],
                                            className='three columns'
                                        ),
                                ],
                                className='row container-display',
                                style={"margin-top": "5%"}
                             ),
                        html.Div(
                                [
                                    html.Div(
                                            [html.P("Local mode", id="mw_fault_text_2_readout", style={"color":"#FF5E5E"})],
                                            className='three columns',
                                            style={"margin-left": "4%"}
                                        ),
                                    html.Div(
                                            [html.P("Gateway comm", id="mw_fault_text_3_readout", style={"color":"#FF5E5E"})],
                                            className='three columns'
                                        ),
                                    html.Div(
                                            [html.P("Temperature fault", id="mw_fault_text_4_readout", style={"color":"#FF5E5E"})],
                                            className='three columns'
                                        ),
                                ],
                                className='row container-display',
                                style={"margin-top": "5%"}
                             ),
                        html.Div(
                                [
                                    html.Div(
                                            [html.P("Internal relay", id="mw_fault_text_5_readout", style={"color":"#FF5E5E"})],
                                            className='three columns',
                                            style={"margin-left": "4%"}
                                        ),
                                    html.Div(
                                            [html.P("fault code: 107", id="mw_fault_text_code_readout", style={"color":"#FF5E5E"})],
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
                                            id='idc_mw_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container",
                                    style={"margin-left": "3%"}
                                ),
                                html.Div(
                                    [html.P("FP: 200 W", id="FP_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("RP: 10 W", id="RP_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("f: 2445.6 MHz", id="freq_text_readout")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("Leak sensors:",)],
                                    className="mini_container",
                                    style={"margin-left": "5%"}
                                ),
                                html.Div(
                                    [daq.Indicator(
                                            id='idc_leak1_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container"
                                ),
                                html.Div(
                                    [daq.Indicator(
                                            id='idc_leak2_sensor_readout',
                                            color="#39ff14",
                                            size=30,
                                            value=True
                                        )],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [daq.Indicator(
                                            id='idc_leak3_sensor_readout',
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
                                id="sensor_readout_graph_mw_power_readout",
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
                                id="readout_graph_mw_freq_readout",
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

    style={"display": "flex", "flex-direction": "column"},
)