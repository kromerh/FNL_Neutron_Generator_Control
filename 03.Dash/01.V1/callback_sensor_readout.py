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


# Functions


VERBOSE = False
VERBOSE_READ_HV = False
VERBOSE_READ_PRESSURE = False
VERBOSE_READ_REFDET = False
VERBOSE_SET_D2FLOW = False
VERBOSE_READ_D2FLOW = False
VERBOSE_SET_FP_SET = False
VERBOSE_READ_MW = False
VERBOSE_SET_FREQ_SET = False

# after this many seconds indicator will turn red
READOUT_DEADTIME = 20

# Functions

# leakage current correction
cwd = os.getcwd()
data_I_leak = pd.read_csv(f'{cwd}/calibration/LUT_leakage_current.csv', index_col=0)
X = data_I_leak['HV_voltage'].values.astype(np.float64)
Y = data_I_leak['HV_current'].values.astype(np.float64)
interp_leak = interp1d(X, Y, fill_value='extrapolate')


# HV calibration
df_HV_LT = pd.read_csv(f'{cwd}/calibration/HV_readout_calibration.txt', delimiter="\t")
interp_HV_voltage = interp1d(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])

# Current calibration
# correct the current that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
df_HV_I_LT =pd.read_csv(f'{cwd}/calibration/I_readout_calibration.txt', delimiter="\t")
# interpolation function
interp_HV_current = interp1d(df_HV_I_LT['Current_read'], df_HV_I_LT['HV_current'])

# dose to neutron output conversion
cwd = os.getcwd()
data_mcnp_LUT = pd.read_csv(f'{cwd}/calibration/LUT_dose_neutron_output.csv', index_col=0)
# position of the sphere is east
interp_dose = interp1d(data_mcnp_LUT.index, data_mcnp_LUT['E'].values, fill_value='extrapolate')


# pressure calibration
# correct the pressure that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
cwd = os.getcwd()
df_LT_pressure = pd.read_csv(f"{cwd}/calibration/LUT_pressure_ion_source.txt", delimiter="\t")

# interpolation function
interp_pressure_IS = interp1d(pd.to_numeric(df_LT_pressure['pressure_IS_pi']).values, pd.to_numeric(df_LT_pressure['pressure_IS_display']).values, fill_value='extrapolate')




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

def get_live_pressure(sql_engine, query_time, verbose=False):
	"""
	Read live_pressure table and return data for that query_time
	"""
	query = f"SELECT * FROM live_pressure WHERE time > \"{query_time}\";"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading live_pressure, retrieved {df.shape} entries.')

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
	[
		Output('live_hv_dose_data_readout', 'data'),
		Output('live_pressure_data_readout', 'data')
	],
	[Input('readout_interval_readout', 'n_intervals')])
def read_live_hv_dose(n):
	# read only the past 5 minutes
	current_time = datetime.datetime.now()
	query_time = current_time - datetime.timedelta(minutes=5)
	query_time = query_time.strftime("%Y-%m-%d %H:%M:%S")

	if sql_engine:
		df_hv_dose = get_live_hv_dose(sql_engine, query_time, verbose=VERBOSE_READ_HV)
		if len(df_hv_dose) > 0:
			df_hv_dose['dose'] = df_hv_dose['dose_voltage'] * 3000 / 5.5

			# current calibration
			df_hv_dose['HV_current'] = interp_HV_current(df_hv_dose['HV_current'].values)
			
			# hv calibration
			df_hv_dose['HV_voltage'] = interp_HV_voltage(df_hv_dose['HV_voltage'].values)
			
			# leakage current correction
			df_hv_dose['HV_current'] = df_hv_dose['HV_current'] - interp_leak(df_hv_dose['HV_voltage'].values)

			idx = df_hv_dose[df_hv_dose['HV_current'] < 0].index # set negative current values to 0
			df_hv_dose.loc[idx, 'HV_current'] = 0

			# compute neutron output from dose
			df_hv_dose['neutron_yield'] = df_hv_dose['dose'].values * (interp_dose(df_hv_dose['HV_voltage'].values) / 100)

		df_pressure = get_live_pressure(sql_engine, query_time, verbose=VERBOSE_READ_PRESSURE)
		if len(df_pressure) > 0:
			df_pressure['pressure_IS'] = 10**(1.667*df_pressure['voltage_IS']-11.33)
			df_pressure['pressure_IS'] = interp_pressure_IS(df_pressure['pressure_IS'])


		json_hv_dose = df_hv_dose.to_json(date_format='iso', orient='split')
		json_pressure = df_pressure.to_json(date_format='iso', orient='split')

		return json_hv_dose, json_pressure


# check the state of the readout, if no new entry in past 15 seconds, make indicator red
@app.callback(
	[
		Output('idc_HV_sensor_readout', 'color'),
		Output('idc_dose_sensor_readout', 'color')
	],	
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_hv_dose_data_readout", "data")])
def set_hv_indicator(readout_interval, live_hv_dose_data):
	if live_hv_dose_data:
		df = pd.read_json(live_hv_dose_data, orient='split')

		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# check last entry
			current_time = datetime.datetime.now()
			query_time = pd.to_datetime((current_time - datetime.timedelta(seconds=READOUT_DEADTIME)))

			last_time = df['time'].values[-1]

			if last_time < query_time:
				return ['red', 'red']
			else:
				return ["#39ff14", "#39ff14"]
		else:
			return ['red', 'red']

	return ["gray", "gray"]





# compute the mean of HV voltage and current for past 10 seconds
@app.callback(
	[Output('HV_kV_text_readout', 'children'),Output('HV_mA_text_readout', 'children')],
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_hv_dose_data_readout", "data")])
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
	Output('experiment_control_data_readout', 'data'),
	[Input('readout_interval_readout', 'n_intervals')])
def read_experiment_control(n):

	if sql_engine:

		df = get_experiment_control_data(sql_engine, verbose=False)

		return df.to_json(date_format='iso', orient='split')


# compute the mean of pressure for past 10 seconds
@app.callback(
	Output('pressure_text_readout', 'children'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_pressure_data_readout", "data")])
def rolling_mean_pressure(readout_interval, live_pressure_data):
	if live_pressure_data:
		df = pd.read_json(live_pressure_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)


			# take only last 10 s
			current_time = datetime.datetime.now()
			query_time = current_time - datetime.timedelta(seconds=10)

			mean = df[ df['time'] > query_time].loc[:, 'pressure_IS'].mean()

			return f"{mean:.2E} mbar"

	else:
		return f"0 mbar"


	return f"0 mbar"


# check the state of the pressure readout, if no new entry in past READOUT_DEADTIME seconds, make indicator red
@app.callback(
	Output('idc_pressure_sensor_readout', 'color'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_pressure_data_readout", "data")])
def set_pressure_indicator(readout_interval, live_pressure_data):
	if live_pressure_data:
		df = pd.read_json(live_pressure_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# check last entry
			current_time = datetime.datetime.now()
			query_time = pd.to_datetime((current_time - datetime.timedelta(seconds=READOUT_DEADTIME)))

			last_time = df['time'].values[-1]

			if last_time < query_time:
				return 'red'
			else:
				return "#39ff14"
		else:
			return 'red'

	return "gray"



# HV graph
@app.callback(
	Output("sensor_readout_graph_HV_readout", "figure"),
	[Input("live_hv_dose_data_readout", "data")],
	[State('experiment_control_data_readout', 'data')]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_HV(json_data, experiment_control_data):
	if experiment_control_data is None:
		raise dash.exceptions.PreventUpdate
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



# Pressure graph
@app.callback(
	Output("sensor_readout_graph_pressure_readout", "figure"),
	[Input("live_pressure_data_readout", "data")],
	[State('experiment_control_data_readout', 'data')]
)
def plot_pressure(json_data, experiment_control_data):
	if experiment_control_data is None:
		raise dash.exceptions.PreventUpdate	

	# y limits for the graph
	experiment_control_data = pd.read_json(experiment_control_data, orient='split')
	lim_max = float(experiment_control_data['pressure_plot_max'].values[0])
	lim_min = float(experiment_control_data['pressure_plot_min'].values[0])

	# print(state_dic)
	traces = []
	if len(experiment_control_data) > 0:
		try:
			df = pd.read_json(json_data, orient='split')

			# HV voltage
			traces.append(go.Scatter(
				x=df['time'],
				y=df['pressure_IS'].values,
				text='Pressure [mbar]',
				line=go.scatter.Line(
					color='red',
					width=1.5
				),
				opacity=0.7,
				name='Pressure [mbar]'
			))

		except:
			traces.append(go.Scatter(
				x=[],
				y=[],
				line=go.scatter.Line(
					color='#42C4F7',
					width=1.0
				),
				text='Pressure',
				# mode='markers',
				opacity=1,
				marker={
					 'size': 15,
					 'line': {'width': 1, 'color': '#42C4F7'}
				},
				mode='lines',
				name='Pressure',

			))

		return {
			'data': traces,
			'layout': go.Layout(
				# xaxis={'title': 'Time'},
				yaxis={'title': 'Pressure [mbar]', 'titlefont': {'color': "red"},
				'type': "log", 'exponentformat':'e', 'side': "right"},
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
		text='Pressure',
		# mode='markers',
		opacity=1,
		marker={
			 'size': 15,
			 'line': {'width': 1, 'color': '#42C4F7'}
		},
		mode='lines',
		name='Pressure',

	))
	return 	{
			'data': traces,
			'layout': go.Layout(
				# xaxis={'title': 'Time'},
				yaxis={'title': 'Pressure [mbar]', 'titlefont': {'color': "red"},
				'type': "log", 'exponentformat':'e', 'side': "right"},
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