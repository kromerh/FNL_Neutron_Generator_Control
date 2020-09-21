import pymysql
import sqlalchemy as sql
import pandas as pd
import datetime
import re
import numpy as np

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
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}

sql_engine = sql.create_engine(connect_string)


# Functions


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









# callback to read the database and store live_hv_dose data in a json objective
@app.callback(
	Output('live_hv_dose_data_readout', 'children'),
	[Input('readout_interval_readout', 'n_intervals')])
def read_live_hv_dose(n):
	# read only the past 5 minutes
	current_time = datetime.datetime.now()
	query_time = current_time - datetime.timedelta(minutes=5)
	query_time = query_time.strftime("%Y-%m-%d %H:%M:%S")

	if sql_engine:

		df = get_live_hv_dose(sql_engine, query_time, verbose=False)

		return df.to_json(date_format='iso', orient='split')





# check the state of the readout, if no new entry in past 15 seconds, make indicator red
@app.callback(
	Output('idc_HV_sensor_readout', 'color'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_hv_dose_data_readout", "children")])
def set_hv_indicator(readout_interval, live_hv_dose_data):
	if live_hv_dose_data:
		df = pd.read_json(live_hv_dose_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# check last entry
			current_time = datetime.datetime.now()
			query_time = pd.to_datetime((current_time - datetime.timedelta(seconds=15)))

			last_time = df['time'].values[-1]

			if last_time < query_time:
				return 'red'
			else:
				return "#39ff14"

	return "#39ff14"





# compute the mean of HV voltage and current for past 10 seconds
@app.callback(
	[Output('HV_kV_text_readout', 'children'),Output('HV_mA_text_readout', 'children')],
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_hv_dose_data_readout", "children")])
def rolling_mean_hv(readout_interval, live_hv_dose_data):
	if live_hv_dose_data:
		df = pd.read_json(live_hv_dose_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# take only last 10 s
			current_time = datetime.datetime.now()
			query_time = current_time - datetime.timedelta(seconds=10)

			mean_HV = df[ df['time'] > query_time].loc[:, 'HV_voltage'].mean()
			mean_I = df[ df['time'] > query_time].loc[:, 'HV_current'].mean()

			return f"-{mean_HV:.1f} kV", f"{mean_I:.1f} mA"

	else:
		return f"-0 kV", f"0 mA"




# callback to read the experiment_control table
@app.callback(
	Output('experiment_control_data_readout', 'children'),
	[Input('readout_interval_readout', 'n_intervals')])
def read_experiment_control(n):

	if sql_engine:

		df = get_experiment_control_data(sql_engine, verbose=False)

		return df.to_json(date_format='iso', orient='split')





# HV graph
@app.callback(
	Output("sensor_readout_graph_HV_readout", "figure"),
	[Input("live_hv_dose_data_readout", "children")],
	[State('experiment_control_data_readout', 'children')]
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
	if len(experiment_control_data) > 0:
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
	return 	{
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



# Refresh experiment id and date when clicking anywhere
@app.callback(
	[
		Output('P_experiment_date_readout', 'children'),
		Output('P_experiment_id_readout', 'children'),
		],
	[Input('sensor_readout_parent', 'n_clicks')])
def click_anywhere(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read the experiment id table in the database
	experiment_id, date = read_experiment_id(sql_engine)

	return f"Experiment date: {date}", f"Experiment ID: {experiment_id}"