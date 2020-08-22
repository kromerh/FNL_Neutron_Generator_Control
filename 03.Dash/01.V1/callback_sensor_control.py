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
import plotly.graph_objs as go

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




VERBOSE = False


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





def get_live_hv_dose(sql_engine, query_time, verbose=False):
	"""
	Read live_hv_dose table and return data for that query_time
	"""
	query = f"SELECT * FROM live_hv_dose WHERE time > \"{query_time}\";"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading live_hv_dose, retrieved {df.shape} entries.')

	return df



def get_experiment_control_data(sql_engine, verbose=False):
	query = f"SELECT * FROM experiment_control;"
	df = pd.read_sql(query, sql_engine)

	if verbose:
		print(f'Getting experiment control.')
		print(df)

	return df








# Callbacks



# callback to read the experiment_control table
@app.callback(
	Output('experiment_control_data', 'children'),
	[Input('readout_interval', 'n_intervals')])
def read_experiment_control(n):

	if sql_engine:

		df = get_experiment_control_data(sql_engine, verbose=False)

		return df.to_json(date_format='iso', orient='split')





# HV graph
@app.callback(
	Output("sensor_control_graph_HV", "figure"),
	[Input("live_hv_dose_data", "children")],
	[State('experiment_control_data', 'children')]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_HV(json_data, experiment_control_data):

	# y limits for the graph
	experiment_control_data = pd.read_json(experiment_control_data, orient='split')
	lim_hv_max = float(experiment_control_data['hv_HV_plot_max'].values[0])
	lim_hv_min = float(experiment_control_data['hv_HV_plot_min'].values[0])

	lim_I_max = float(experiment_control_data['hv_I_plot_max'].values[0])
	lim_I_min = float(experiment_control_data['hv_I_plot_min'].values[0])

	# print(state_dic)
	traces = []

	try:
		df = pd.read_json(json_data, orient='split')
		# HV voltage
		traces.append(go.Scatter(
			x=df['time'],
			y=df['HV_voltage'],
			text='HV_voltage [-kV]',
			line=go.scatter.Line(
				color='red',
				width=1.5
			),
			opacity=0.7,
			name='HV_voltage [-kV]'
		))
		# HV current
		traces.append(go.Scatter(
			x=df['time'],
			y=df['HV_current'],
			text='HV_current [-mA]',
			line=go.scatter.Line(
				color='blue',
				width=1.5
			),
			opacity=0.7,

			name='HV_current [-mA]',
			yaxis='y2'
		))

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='HV',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='HV',

		))

	return {
		'data': traces,
		'layout': go.Layout(
			# xaxis={'title': 'Time'},
			yaxis={'title': 'HV [-kV]', 'range': [lim_hv_min, lim_hv_max], 'titlefont': {'color': "red"}},
			yaxis2={'title': 'I [-mA]', 'range': [lim_I_min, lim_I_max], "overlaying": "y", 'side': "right", 'titlefont': {'color': "blue"}},
            height=200,  # px
            showlegend=False,
            margin=dict(t=10, b=15, l=50, r=50),
			hovermode='closest'
		)
	}





# callback to read the database and store live_hv_dose data in a json objective
@app.callback(
	Output('live_hv_dose_data', 'children'),
	[Input('readout_interval', 'n_intervals')])
def read_live_hv_dose(n):
	# read only the past 5 minutes
	current_time = datetime.datetime.now()
	query_time = current_time - datetime.timedelta(minutes=5)
	query_time = query_time.strftime("%Y-%m-%d %H:%M:%S")

	if sql_engine:

		df = get_live_hv_dose(sql_engine, query_time, verbose=False)

		return df.to_json(date_format='iso', orient='split')




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