import pymysql
import sqlalchemy as sql

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq

layout_sensor_readout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
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
                        html.P("Experiment date: 2020-08-01 10:00", style={"color":'red'}),
                        html.P("Experiment ID: 99", style={"color":'red'}),
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
                                    style={"margin-left": "3%"}
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
                                    [daq.NumericInput(id='d2flow_input',value=1000, max=4000, min=0, size=120,label='mV', labelPosition='right')],
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
                                id="sensor_readout_graph_HV",
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
                                id="sensor_readout_graph_dose",
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
                                id="sensor_readout_graph_pressure",
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
                                id="sensor_readout_graph_d2flow",
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
                                            [daq.NumericInput(id='FP_input',value=200, max=200, min=0, size=80,label='W', labelPosition='right')],
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
                                            [html.P("freq setpoint 2450.0 MHz", id="mw_setpoint_freq_text")],
                                            style={"margin-left": "4%", "margin-top": "1%"}
                                        ),
                                    html.Div(
                                            [html.P("Freq input:")],
                                            style={"margin-left": "10%", "margin-top": "1%"}
                                        ),
                                    html.Div(
                                            [daq.NumericInput(id='freq_input',value=2450, max=2500, min=2400, size=80,label='MHz', labelPosition='right')],
                                            # style={"margin-left": "80%"}
                                        ),
                                html.Div(
                                    [html.Button('Send', id='btn_freq_set', n_clicks=0)],
                                    style={"margin-left": "4%"}

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
                                id="sensor_readout_graph_mw_power",
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
                                id="sensor_readout_graph_mw_freq",
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
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)