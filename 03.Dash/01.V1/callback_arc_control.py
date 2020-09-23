import pymysql
import sqlalchemy as sql
import pandas as pd
import datetime
import re
import numpy as np
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

from app import app

from scipy.interpolate import interp1d

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


def send_to_DB(sql_engine, speed, direction):

	query = f"""UPDATE arc_motor_control SET speed=\"{speed}\", direction=\"{direction}\" WHERE arc_motor_control.id=1;"""
	sql_engine.execute(query)


def read_last_commands(sql_engine, limit=10):

	query = f"""SELECT * FROM arc_motor_log ORDER BY id DESC LIMIT {limit};"""
	df = pd.read_sql(query, sql_engine)

	return df




# Update log table
@app.callback([
				Output('tbl_log', 'data'),
				Output('tbl_log', 'columns')
				],
			  [Input('readout_interval', 'n_intervals')])
def update_log(n_intervals):
	df = read_last_commands(sql_engine, limit=10)

	columns = [{"name": i, "id": i} for i in df.columns]
	data = df.to_dict("records")

	return data, columns



# Update LED when knob is turned
@app.callback([Output('disp_speed', 'value'),Output('disp_direction', 'value')],
			  [Input('knob_speed', 'value'), Input('knob_direction', 'value')])
def update_LEDs(knob_speed, knob_direction):
	if (knob_speed is None) and (knob_direction is None):
		raise dash.exceptions.PreventUpdate
	return int(knob_speed), int(knob_direction)




# Click on button to send speed and direction to database
@app.callback(Output('P_send', 'children'),
			  [Input('btn_send', 'n_clicks')],
			  [State('disp_speed', 'value'), State('disp_direction', 'value')])
def send_to_db(btn_send, disp_speed, disp_direction):
	if btn_send is None:
		raise dash.exceptions.PreventUpdate

	send_to_DB(sql_engine, disp_speed, disp_direction)

	return f"Send speed {disp_speed}, direction {disp_direction}"



# Click on button stop to send 0 speed and direction
@app.callback(Output('dump_btn_stop', 'children'),
			  [Input('btn_stop', 'n_clicks')])
def send_to_db(btn_stop):
	if btn_stop is None:
		raise dash.exceptions.PreventUpdate

	print("Send speed 0 direction 0")
	send_to_DB(sql_engine, 0, 0)

	return None