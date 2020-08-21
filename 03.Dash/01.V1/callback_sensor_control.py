import pymysql
import sqlalchemy as sql
import pandas as pd
import datetime
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app


# Connect to the database

# read password and user to database
credentials_file = r'../../credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]

host="localhost"  # your host
user=user # username
passwd=pw  # password
db="FNL" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}

sql_engine = sql.create_engine(connect_string)


# Functions



def read_experiment_id_table(sql_engine, experiment_id=None):
	"""
	Reads the experiment_id table and returns the id and the date as dataframe.
	"""
	if experiment_id:
		query = f"SELECT * FROM experiment WHERE id = \"{experiment_id}\";"
		df = pd.read_sql(query, sql_engine)
		if len(df) > 0:
			df['date'] = pd.to_datetime(df['date'].values)
			df['date'] = df['date'].dt.strftime("%Y-%m-%d %H:%M")

			return df

	else:
		query = f"SELECT * FROM experiment ORDER BY id DESC;"
		df = pd.read_sql(query, sql_engine)
		df['date'] = pd.to_datetime(df['date'].values)
		df['date'] = df['date'].dt.strftime("%Y-%m-%d %H:%M")

		# print(df.head())
		return df


def set_experiment_id(sql_engine, experiment_id, verbose=False):
	"""
	Updates the experiment ID int he control table
	"""
	if experiment_id:
		query = f"""UPDATE experiment_control SET experiment_id={experiment_id};"""

		if verbose: print(query)
		sql_engine.execute(sql.text(query))




def set_mw_ip(sql_engine, ip, verbose=False):
	"""
	Set ip of the microwave in the experiment control table
	"""
	if ip:
		t_ = re.findall(r'([a-zA-z])+', ip)
		if len(t_) > 0:
			if verbose: print(t_)
			if verbose: print(f"Non digits in ip! {ip}")

			return -1

		t_ = re.findall(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', ip)
		if len(t_[0]) != 4:
			if verbose: print(t_[0])
			if verbose: print(f"Not four digits between points! {ip}")
			return -1
		else:
			for i in t_[0]:
				if int(i) > 255:
					if verbose: print(t_[0])
					if verbose: print(f"IP contains number larger 255! {ip}")
					return -1

		query = f"""UPDATE experiment_control SET mw_ip=\"{ip}\";"""

		if verbose: print(query)
		sql_engine.execute(sql.text(query))


def read_experiment_id(sql_engine):
	"""
	Reads the experiment_id from the experiment_control table and the corresponding date and returns both
	"""

	query = f"SELECT experiment_id FROM experiment_control;"
	df = pd.read_sql(query, sql_engine)

	experiment_id = df['experiment_id'].values[0]

	query = f"SELECT date FROM experiment WHERE id = {experiment_id};"
	df = pd.read_sql(query, sql_engine)
	date = df['date'].dt.strftime("%Y-%m-%d %H:%M").values[0]

	return experiment_id, date


def read_mw_ip(sql_engine):
	"""
	Reads the microwave ip from the control table and returns it
	"""

	query = f"SELECT mw_ip FROM experiment_control;"
	df = pd.read_sql(query, sql_engine)

	ip = df['mw_ip'].values[0]

	return ip











# Callbacks



# Copy SSH for reference detector
@app.callback(
	Output('btn_copy_ssh_refDet_output', 'value'),
	[Input('btn_copy_ssh_refDet', 'n_clicks')],)
def clipboard_refDet_ssh(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	df=pd.DataFrame(['ssh pi@pi-neutimag-due4'])
	df.to_clipboard(index=False,header=False)

	return df.to_json()



# Set the microwave generator ip address in the experiment control table
@app.callback(
	Output('output_mw_ip', 'value'),
	[Input('btn_experiment_control_mw_ip', 'n_clicks')],
	[State('sensor_control_mw_ip_input', 'value')])
def update_mw_ip(n_clicks, ip):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate
	if ip != "255.255.255.255":
		set_mw_ip(sql_engine, ip, verbose=False)

		return ip


# Load the current settings from control table
@app.callback(
	[
		Output('sensor_control_mw_ip_input', 'value'),
		Output('sensor_control_dropdown_ID', 'value'),
	],
	[Input('btn_experiment_control_read_control', 'n_clicks')])
def load_current_control(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	experiment_id, date = read_experiment_id(sql_engine)

	ip = read_mw_ip(sql_engine)

	return ip, experiment_id

# Refresh the current experiment id and date when it was selected in the dropdown
@app.callback(
	[
		Output('P_experiment_date', 'children'),
		Output('P_experiment_id', 'children'),
	],
	[Input('sensor_control_dropdown_ID', 'value')])
def update_experiment_id_date(experiment_id):

	df = read_experiment_id_table(sql_engine, experiment_id=experiment_id)
	if len(df) > 0:
		date = df['date'].values[0]

		# update in the control table
		set_experiment_id(sql_engine, experiment_id, verbose=False)

		# set in the html.P
		return f"Experiment date: {date}", f"Experiment ID: {experiment_id}"



# Refresh experiment id and date table when clicking anywhere
# Update tag dropdowns when clicking anywhere
@app.callback(
	[
		Output('experiment_id_table_sensor_control', 'columns'),
		Output('experiment_id_table_sensor_control', 'data'),
		Output('sensor_control_dropdown_ID', 'options'),
	],
	[Input('sensor_control_parent', 'n_clicks')])
def click_anywhere(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read the experiment id table in the database
	df = read_experiment_id_table(sql_engine)

	columns = [{"name": i, "id": i} for i in df.columns]
	data = df.to_dict('records')

	# what to display as the dropdown options
	options_ids=[
				{'label': i, 'value': i} for i in df['id'].values
			]

	return columns, data, options_ids