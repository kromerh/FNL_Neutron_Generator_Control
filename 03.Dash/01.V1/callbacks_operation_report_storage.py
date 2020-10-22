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


def get_storage_hv_dose(sql_engine, verbose=False):
	"""
	Read live_hv_dose table and return data for that query_time
	"""
	query = f"SELECT * FROM storage_hv_dose;"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading storage_hv_dose, retrieved {df.shape} entries.')

	return df


def get_storage_pressure(sql_engine, verbose=False):
	"""
	Read storage_pressure table and return data for that query_time
	"""
	query = f"SELECT * FROM storage_pressure;"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading storage_pressure, retrieved {df.shape} entries.')

	return df


def get_storage_refDet(sql_engine, verbose=False):
	"""
	Read storage_ref_det table and return data for that query_time
	"""
	query = f"SELECT * FROM storage_ref_det;"
	df = pd.read_sql(query, sql_engine)
	df['sum_counts'] = df[['counts_D1', 'counts_D2', 'counts_D3', 'counts_D4']].sum(axis=1)

	if verbose: print(f'Reading storage_ref_det, retrieved {df.shape} entries. \n {df.head()}')

	return df


def get_storage_d2flow(sql_engine, verbose=False):
	"""
	Read storage_d2flow table and return data for that query_time
	"""
	query = f"SELECT * FROM storage_d2flow;"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading storage_d2flow, retrieved {df.shape} entries. \n {df.head()}')

	return df


def get_storage_mw(sql_engine, verbose=False):
	"""
	Read storage_d2flow table and return data for that query_time
	"""
	query = f"SELECT * FROM storage_mw;"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading storage_mw, retrieved {df.shape} entries. \n {df.head()}')

	return df

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








# plot hv
@app.callback(
	Output("graph_HV_storage", "figure"),
	[Input('btn_storage_load_and_plot', 'n_clicks')])
def plot_hv(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# load data from database
	df_hv_dose = get_live_hv_dose(sql_engine, verbose=False)

	traces = []

	if len(df_hv_dose) > 0:

		# current calibration
		df_hv_dose['HV_current'] = interp_HV_current(df_hv_dose['HV_current'].values)

		# hv calibration
		df_hv_dose['HV_voltage'] = interp_HV_voltage(df_hv_dose['HV_voltage'].values)

		# leakage current correction
		df_hv_dose['HV_current'] = df_hv_dose['HV_current'] - interp_leak(df_hv_dose['HV_voltage'].values)

		idx = df_hv_dose[df_hv_dose['HV_current'] < 0].index # set negative current values to 0
		df_hv_dose.loc[idx, 'HV_current'] = 0

		df = df_hv_dose[['time', 'HV_voltage', 'HV_current']]

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

	else:

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
				yaxis={'title': 'HV [-kV]', 'range': [0, 150], 'titlefont': {'color': "red"}},
				yaxis2={'title': 'I [-mA]', 'range': [0, 2], "overlaying": "y", 'side': "right", 'titlefont': {'color': "blue"}},
				height=200,  # px
				showlegend=False,
				margin=dict(t=10, b=15, l=50, r=50),
				hovermode='closest'
			)
		}



# plot dose
@app.callback(
	Output("graph_dose_storage", "figure"),
	[Input('btn_storage_load_and_plot', 'n_clicks')])
def plot_hv(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# load data from database
	df_hv_dose = get_live_hv_dose(sql_engine, verbose=False)
	df_refDet = get_live_refDet(sql_engine, verbose=False)

	traces = []

	if len(df_hv_dose) > 0:
		plot_hv = True
		plot_dose = True
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
		df_dose = df_hv_dose


		if len(df_dose) == 0:
			df_dose['time'] = datetime.datetime.now()
			df_dose['neutron_yield'] = -1
		if len(df_refDet) == 0:
			df_refDet['time'] = datetime.datetime.now()
			df_refDet['sum_counts'] = -1
		# refDet
		traces.append(go.Scatter(
			x=df_refDet['time'],
			y=df_refDet['sum_counts'],
			text='Counts [30s]',
			line=go.scatter.Line(
				color='orange',
				width=1.5
			),
			opacity=0.7,
			name='Counts [30s]'
		))
		# Output
		traces.append(go.Scatter(
			x=df_dose['time'],
			y=df_dose['neutron_yield'],
			text='Neutron yield',
			line=go.scatter.Line(
				color='blue',
				width=1.5
			),
			opacity=0.7,

			name='Neutron yield',
			yaxis='y2'
		))

	else:

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
			name='Dose and ref det',

		))

	return 	{
			'data': traces,
			'layout': go.Layout(
				# xaxis={'title': 'Time'},
				yaxis={'title': 'Counts [30s]', 'range': [0, 2000], 'side': "left" ,'titlefont': {'color': "orange"}},
				yaxis2={'title': 'Neutron yield', 'range': [1e6, 1e8], 'exponentformat':'e', "overlaying": "y", 'side': "right", 'titlefont': {'color': "blue"}},

				height=200,  # px
				showlegend=False,
				margin=dict(t=10, b=15, l=50, r=50),
				hovermode='closest'
			)
		}

# plot pressure
@app.callback(
	Output("graph_pressure_storage", "figure"),
	[Input('btn_storage_load_and_plot', 'n_clicks')])
def plot_pressure(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# load data from database
	df_pressure = get_live_pressure(sql_engine, verbose=False)

	traces = []


	if len(df_pressure) > 0:
		df_pressure['pressure_IS'] = 10**(1.667*df_pressure['voltage_IS']-11.33)
		df_pressure['pressure_IS'] = interp_pressure_IS(df_pressure['pressure_IS'])

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

	else:

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


# plot d2flow
@app.callback(
	Output("graph_d2flow_storage", "figure"),
	[Input('btn_storage_load_and_plot', 'n_clicks')])
def plot_d2flow(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# load data from database
	df_d2flow = get_live_d2flow(sql_engine, verbose=False)

	traces = []


	if len(df_d2flow) > 0:

		# HV voltage
		traces.append(go.Scatter(
			x=df['time'],
			y=df['voltage_flow'],
			text='Flow measured [mV]',
			line=go.scatter.Line(
				color='red',
				width=1.5
			),
			opacity=0.7,
			name='Flow measured [mV]'
		))
		# HV current
		traces.append(go.Scatter(
			x=df['time'],
			y=df['voltage_flow_set'],
			text='Flow set [mV]',
			line=go.scatter.Line(
				color='green',
				width=1.5
			),
			opacity=0.7,

			name='Flow set [mV]',
			yaxis='y2'
		))

	else:

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
			name='Flow',

		))

	return {
		'data': traces,
		'layout': go.Layout(
			# xaxis={'title': 'Time'},
			yaxis={'title': 'Flow measured [mV]', 'titlefont': {'color': "red"}},
			yaxis2={'title': 'Flow set [mV]',  "range": [0, 1000], "overlaying": "y", 'side': "right", 'titlefont': {'color': "green"}},
			height=200,  # px
			showlegend=False,
			margin=dict(t=10, b=15, l=50, r=50),
			hovermode='closest'
		)
	}


# plot mw_power
@app.callback(
	Output("graph_mw_power_storage", "figure"),
	[Input('btn_storage_load_and_plot', 'n_clicks')])
def plot_mw_power(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# load data from database
	df_mw = get_live_mw(sql_engine, verbose=False)

	traces = []


	if len(df_mw) > 0:
		# FP
		traces.append(go.Scatter(
			x=df['time'],
			y=df['FP'],
			text='Forward power [W]',
			line=go.scatter.Line(
				color='blue',
				width=1.5
			),
			opacity=0.7,
			name='Forward power [W]'
		))
		# FP set
		traces.append(go.Scatter(
			x=df['time'],
			y=df['FP_set'],
			text='Forward power setpoint [W]',
			line=go.scatter.Line(
				color='green',
				width=1.5
			),
			opacity=0.7,

			name='Forward power setpoint [W]',
		))
		# RP
		traces.append(go.Scatter(
			x=df['time'],
			y=df['RP'],
			text='Reflected power [W]',
			line=go.scatter.Line(
				color='red',
				width=1.5
			),
			opacity=0.7,

			name='Reflected power [W]',
			yaxis='y2'
		))

	else:

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
			name='mw power',

		))

	return {
		'data': traces,
		'layout': go.Layout(
			# xaxis={'title': 'Time'},
			yaxis={'title': 'FP [W]', "range": [0, 205], 'side': "right", 'titlefont': {'color': "black"}},
			yaxis2={'title': 'RP [W]',  "range": [0, 100], "overlaying": "y", 'side': "left", 'titlefont': {'color': "red"}},
			height=150,  # px
			showlegend=False,
			margin=dict(t=10, b=15, l=50, r=50),
			hovermode='closest'
		)
	}





# plot mw_freq
@app.callback(
	Output("graph_mw_freq_storage", "figure"),
	[Input('btn_storage_load_and_plot', 'n_clicks')])
def plot_mw_freq(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# load data from database
	df_mw = get_live_mw(sql_engine, verbose=False)

	traces = []


	if len(df_mw) > 0:
		# FP
		traces.append(go.Scatter(
			x=df['time'],
			y=df['Freq'],
			text='Frequency [MHz]',
			line=go.scatter.Line(
				color='blue',
				width=1.5
			),
			opacity=0.7,
			name='Frequency [MHz]'
		))
		# FP set
		traces.append(go.Scatter(
			x=df['time'],
			y=df['Freq_set'],
			text='Frequency setpoint [MHz]',
			line=go.scatter.Line(
				color='green',
				width=1.5
			),
			opacity=0.7,

			name='Frequency setpoint [MHz]',
		))

	else:

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
			name='mw freq',

		))

	return {
		'data': traces,
		'layout': go.Layout(
			# xaxis={'title': 'Time'},
			yaxis={'title': 'Frequency [MHz]', "range": [2350, 2550], 'side': "right", 'titlefont': {'color': "black"}},
			height=150,  # px
			showlegend=False,
			margin=dict(t=10, b=15, l=50, r=50),
			hovermode='closest'
		)
	}


# Refresh overview table when clicking button
@app.callback(
	[
		Output('tbl_storage_overview', 'columns'),
		Output('tbl_storage_overview', 'data'),
		Output('dropdown_dates', 'options')
	],
	[Input('btn_storage_overview', 'n_clicks')])
def refresh_dates(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read number of entries in each table
	query = "SELECT DATE(time) as date, count(id) as count_hv_dose FROM storage_hv_dose GROUP BY DATE(time)"
	df_hv_dose = pd.read_sql(query, sql_engine)

	# read number of entries in each table
	query = "SELECT DATE(time) as date, count(id) as count_pressure FROM storage_pressure GROUP BY DATE(time)"
	df_pressure = pd.read_sql(query, sql_engine)

	# read number of entries in each table
	query = "SELECT DATE(time) as date, count(id) as count_d2flow FROM storage_d2flow GROUP BY DATE(time)"
	df_d2flow = pd.read_sql(query, sql_engine)

	# read number of entries in each table
	query = "SELECT DATE(time) as date, count(id) as count_ref_det FROM storage_ref_det GROUP BY DATE(time)"
	df_ref_det = pd.read_sql(query, sql_engine)

	# read number of entries in each table
	query = "SELECT DATE(time) as date, count(id) as count_mw FROM storage_mw GROUP BY DATE(time)"
	df_mw = pd.read_sql(query, sql_engine)

	dfs = [df_hv_dose, df_pressure, df_d2flow, df_ref_det, df_mw]
	df = dfs[0]
	for ii in range(0, len(dfs)-1):
	    df = df.merge(dfs[ii+1], left_on='date', right_on='date', how='outer')

	columns = [{"name": i, "id": i} for i in df.columns]
	data = df.to_dict('records')

	# what to display as the dropdown options
	options_ids=[
				{'label': i, 'value': i} for i in df['date'].values
			]


	return columns, data, options_dates