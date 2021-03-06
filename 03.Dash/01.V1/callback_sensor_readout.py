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
credentials_file = f'{os.getcwd()}/FNL_Neutron_Generator_Control/credentials.pw'

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
data_I_leak = pd.read_csv(f'{cwd}/FNL_Neutron_Generator_Control/03.Dash/01.V1/calibration/LUT_leakage_current.csv', index_col=0)
X = data_I_leak['HV_voltage'].values.astype(np.float64)
Y = data_I_leak['HV_current'].values.astype(np.float64)
interp_leak = interp1d(X, Y, fill_value='extrapolate')


# HV calibration
df_HV_LT = pd.read_csv(f'{cwd}/FNL_Neutron_Generator_Control/03.Dash/01.V1/calibration/HV_readout_calibration.txt', delimiter="\t")
interp_HV_voltage = interp1d(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])

# Current calibration
# correct the current that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
df_HV_I_LT =pd.read_csv(f'{cwd}//FNL_Neutron_Generator_Control/03.Dash/01.V1/calibration/I_readout_calibration.txt', delimiter="\t")
# interpolation function
interp_HV_current = interp1d(df_HV_I_LT['Current_read'], df_HV_I_LT['HV_current'])

# dose to neutron output conversion
cwd = os.getcwd()
data_mcnp_LUT = pd.read_csv(f'{cwd}//FNL_Neutron_Generator_Control/03.Dash/01.V1/calibration/LUT_dose_neutron_output.csv', index_col=0)
# position of the sphere is east
interp_dose = interp1d(data_mcnp_LUT.index, data_mcnp_LUT['E'].values, fill_value='extrapolate')


# pressure calibration
# correct the pressure that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
cwd = os.getcwd()
df_LT_pressure = pd.read_csv(f"{cwd}//FNL_Neutron_Generator_Control/03.Dash/01.V1/calibration/LUT_pressure_ion_source.txt", delimiter="\t")

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

def get_live_refDet(sql_engine, query_time, verbose=False):
	"""
	Read live_ref_det table and return data for that query_time
	"""
	query = f"SELECT * FROM live_ref_det WHERE time > \"{query_time}\";"
	df = pd.read_sql(query, sql_engine)
	df['sum_counts'] = df[['counts_D1', 'counts_D2', 'counts_D3', 'counts_D4']].sum(axis=1)

	if verbose: print(f'Reading live_ref_det, retrieved {df.shape} entries. \n {df.head()}')

	return df


def get_live_d2flow(sql_engine, query_time, verbose=False):
	"""
	Read live_d2flow table and return data for that query_time
	"""
	query = f"SELECT * FROM live_d2flow WHERE time > \"{query_time}\";"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading live_d2flow, retrieved {df.shape} entries. \n {df.head()}')

	return df


def get_live_mw(sql_engine, query_time, verbose=False):
	"""
	Read live_d2flow table and return data for that query_time
	"""
	query = f"SELECT * FROM live_mw WHERE time > \"{query_time}\";"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading live_mw, retrieved {df.shape} entries. \n {df.head()}')

	return df


def get_live_leak(sql_engine, query_time, verbose=False):
	"""
	Read live_leak table and return data for that query_time
	"""
	query = f"SELECT * FROM live_leak WHERE time > \"{query_time}\";"
	df = pd.read_sql(query, sql_engine)

	if verbose: print(f'Reading live_leak, retrieved {df.shape} entries. \n {df.head()}')

	return df







# Callbacks









# callback to read the database and store live_hv_dose data in a json objective
@app.callback(
	[
		Output('live_hv_dose_data_readout', 'data'),
		Output('live_refDet_data_readout', 'data'),
		Output('live_pressure_data_readout', 'data'),
		Output('live_d2flow_data_readout', 'data'),
		Output('live_mw_data_readout', 'data'),
		Output('live_leak_data_readout', 'data')
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

		df_refDet = get_live_refDet(sql_engine, query_time, verbose=VERBOSE_READ_REFDET)
		df_d2flow = get_live_d2flow(sql_engine, query_time, verbose=VERBOSE_READ_D2FLOW)
		df_mw = get_live_mw(sql_engine, query_time, verbose=VERBOSE_READ_MW)
		df_leak = get_live_leak(sql_engine, query_time, verbose=VERBOSE_READ_MW)

		json_hv_dose = df_hv_dose.to_json(date_format='iso', orient='split')
		json_pressure = df_pressure.to_json(date_format='iso', orient='split')

		json_refDet = df_refDet.to_json(date_format='iso', orient='split')
		json_d2flow = df_d2flow.to_json(date_format='iso', orient='split')
		json_mw = df_mw.to_json(date_format='iso', orient='split')
		json_leak = df_leak.to_json(date_format='iso', orient='split')

		return json_hv_dose, json_refDet, json_pressure, json_d2flow, json_mw, json_leak


# check the state of the pressure readout, if no new entry in past READOUT_DEADTIME seconds, make indicator red
@app.callback(
	Output('idc_d2flow_sensor_readout', 'color'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_d2flow_data_readout", "data")])
def set_pressure_indicator(readout_interval, live_d2flow_data):
	if live_d2flow_data:
		df = pd.read_json(live_d2flow_data, orient='split')
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



# check the state of the refDet readout, if no new entry in past READOUT_DEADTIME seconds, make indicator red
@app.callback(
	Output('idc_refDet_sensor_readout', 'color'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_refDet_data_readout", "data")])
def set_refDet_indicator(readout_interval, live_refDet_data):
	if live_refDet_data:
		df = pd.read_json(live_refDet_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# check last entry
			current_time = datetime.datetime.now()
			query_time = pd.to_datetime((current_time - datetime.timedelta(seconds=35+READOUT_DEADTIME)))

			last_time = df['time'].values[-1]

			if last_time < query_time:
				return 'red'
			else:
				return "#39ff14"
		else:
			return 'red'
	return "gray"





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

# check the state of the mw readout, if no new entry in past READOUT_DEADTIME seconds, make indicator red
@app.callback(
	Output('idc_mw_sensor_readout', 'color'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_mw_data_readout", "data")])
def set_mw_indicator(readout_interval, live_mw_data):
	if live_mw_data:
		df = pd.read_json(live_mw_data, orient='split')
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


# check the state of the leak sensor readouts
# if a 0 in the past 60 seconds, make red
@app.callback(
	[
		Output('idc_leak1_sensor_readout', 'color'),
		Output('idc_leak2_sensor_readout', 'color'),
		Output('idc_leak3_sensor_readout', 'color')
	],
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_leak_data_readout", "data")])
def set_leak_indicators(readout_interval, live_leak_data_readout):
	if live_leak_data_readout:
		df = pd.read_json(live_leak_data_readout, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# check last entry
			current_time = datetime.datetime.now()
			query_time = pd.to_datetime((current_time - datetime.timedelta(seconds=READOUT_DEADTIME)))

			last_time = df['time'].values[-1]

			if last_time < query_time:
				return ['red', 'red', 'red']
			else:
				color_s1 = 'red'
				color_s3 = 'red'
				color_s2 = 'red'

				query_time = pd.to_datetime((current_time - datetime.timedelta(seconds=60)))
				df = df[ df['time'] >= query_time ]


				counts_s1 = df['s1'].shape[0]
				counts_s2 = df['s2'].shape[0]
				counts_s3 = df['s3'].shape[0]

				if counts_s1 == df['s1'].sum(): 
					color_s1 = "#39ff14"
				if counts_s2 == df['s2'].sum(): 
					color_s2 = "#39ff14"
				if counts_s3 == df['s3'].sum(): 
					color_s3 = "#39ff14"

				return [color_s1, color_s2, color_s3]
		else:
			return ["red", "red", "red"]

	return ["gray", "gray", "gray"]




# compute the mean of mw power and freq for past 10 seconds
@app.callback(
	[Output('FP_text_readout', 'children'),Output('RP_text_readout', 'children'),Output('freq_text_readout', 'children')],
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_mw_data_readout", "data")])
def rolling_mean_mw(readout_interval, live_mw_data):
	if live_mw_data:
		df = pd.read_json(live_mw_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# take only last 10 s
			current_time = datetime.datetime.now()
			query_time = current_time - datetime.timedelta(seconds=10)

			mean_fp = df[ df['time'] > query_time].loc[:, 'FP'].mean()
			mean_rp = df[ df['time'] > query_time].loc[:, 'RP'].mean()
			mean_freq = df[ df['time'] > query_time].loc[:, 'Freq'].mean() / 10

			return f"{mean_fp:.1f} W", f"{mean_rp:.1f} W", f"{mean_freq:.1f} MHz"

	else:
		return f"0 W", f"0 W",  f"0 MHz"


	return f"0 W", f"0 W", f"0 MHz"


# compute the mean of dose and neutron yield for past 10 seconds
@app.callback(
	[Output('dose_text_readout', 'children'),Output('yield_text_readout', 'children')],
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_hv_dose_data_readout", "data")])
def rolling_mean_dose(readout_interval, live_hv_dose_data):
	if live_hv_dose_data:
		df = pd.read_json(live_hv_dose_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)
			# take only last 10 s
			current_time = datetime.datetime.now()
			query_time = current_time - datetime.timedelta(seconds=10)

			mean_dose = df[ df['time'] > query_time].loc[:, 'dose'].mean()
			mean_yield = df[ df['time'] > query_time].loc[:, 'neutron_yield'].mean()

			return f"{mean_dose:.0f} muSv/h", f"{mean_yield:.1E} 1/s"

	else:
		return f"0 muSv/h", f"0 1/s"


	return f"0 muSv/h", f"0 1/s"



# read back the FP setpoint and display it
@app.callback(
	Output('mw_setpoint_FP_text_readout', 'children'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("experiment_control_data_readout", "data")])
def set_FP_setpoint_text(readout_interval, experiment_control_data):
	if experiment_control_data:
		df = pd.read_json(experiment_control_data, orient='split')
		if len(df) > 0:
			fp_set = int(df['mw_fp_set'].values[0])

			return f"FP setpoint {fp_set} W"

	else:
		return f"FP setpoint 0 W"


	return f"FP setpoint 0 W"



# read back the freq setpoint and display it
@app.callback(
	Output('mw_setpoint_freq_text_readout', 'children'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("experiment_control_data_readout", "data")])
def set_FREQ_setpoint_text(readout_interval, experiment_control_data):
	if experiment_control_data:
		df = pd.read_json(experiment_control_data, orient='split')
		if len(df) > 0:
			mw_freq_set = float(df['mw_freq_set'].values[0])

			return f"Freq setpoint {mw_freq_set:.1f} MHz"

	else:
		return f"Freq setpoint 0 MHz"


	return f"Freq setpoint 0 MHz"




# compute the mean of flow for past 10 seconds
@app.callback(
	Output('d2flow_text_readout', 'children'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_d2flow_data_readout", "data")])
def rolling_mean_d2flow(readout_interval, live_d2flow_data):
	if live_d2flow_data:
		df = pd.read_json(live_d2flow_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)


			# take only last 10 s
			current_time = datetime.datetime.now()
			query_time = current_time - datetime.timedelta(seconds=10)

			mean = df[ df['time'] > query_time].loc[:, 'voltage_flow'].mean()

			return f"{mean:.0f} mV"

	else:
		return f"0 mV"


	return f"0 mV"




# compute the mean of refDet counts for past 60 seconds
@app.callback(
	Output('refDet_text_readout', 'children'),
	[Input('readout_interval_readout', 'n_intervals')],
	[State("live_refDet_data_readout", "data")])
def rolling_mean_refDet(readout_interval, live_refDet_data):
	if live_refDet_data:
		df = pd.read_json(live_refDet_data, orient='split')
		if len(df) > 0:
			df['time'] = pd.to_datetime(df['time'])
			df['time'] = df['time'].dt.tz_localize(None)


			# take only last 10 s
			current_time = datetime.datetime.now()
			query_time = current_time - datetime.timedelta(seconds=60)

			mean = df[ df['time'] > query_time].loc[:, 'sum_counts'].mean()
			if np.isnan(mean): mean = 0
			return f"{int(mean)} /30s"

	else:
		return f"0 /30s"


	return f"0 /30s"





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

# dose graph
@app.callback(
	Output("sensor_readout_graph_dose_readout", "figure"),
	[Input("live_hv_dose_data_readout", "data"), Input("live_refDet_data_readout", "data")],
	[State('experiment_control_data_readout', 'data')]
)
def plot_dose(json_data_hv_dose, json_data_refDet, experiment_control_data):

	# y limits for the graph
	experiment_control_data = pd.read_json(experiment_control_data, orient='split')
	lim_refDet_max = float(experiment_control_data['refDet_plot_max'].values[0])
	lim_refDet_min = float(experiment_control_data['refDet_plot_min'].values[0])

	lim_yield_max = float(experiment_control_data['yield_plot_max'].values[0])
	lim_yield_min = float(experiment_control_data['yield_plot_min'].values[0])


	# print(state_dic)
	traces = []
	if len(experiment_control_data) > 0:
		try:
			df_dose = pd.read_json(json_data_hv_dose, orient='split')
			df_refDet = pd.read_json(json_data_refDet, orient='split')
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

		except:
			traces.append(go.Scatter(
				x=[],
				y=[],
				line=go.scatter.Line(
					color='orange',
					width=1.0
				),
				text='Counts [30s]',
				# mode='markers',
				opacity=1,
				marker={
					 'size': 15,
					 'line': {'width': 1, 'color': 'orange'}
				},
				mode='lines',
				name='Counts [30s]',

			))

		return {
			'data': traces,
			'layout': go.Layout(
				# xaxis={'title': 'Time'},
				yaxis={'title': 'Counts [30s]', 'range': [lim_refDet_min, lim_refDet_max], 'side': "left" ,'titlefont': {'color': "orange"}},
				yaxis2={'title': 'Neutron yield', 'range': [lim_yield_min, lim_yield_max], 'exponentformat':'e', "overlaying": "y", 'side': "right", 'titlefont': {'color': "blue"}},

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
		text='Counts [30s]',
		# mode='markers',
		opacity=1,
		marker={
			 'size': 15,
			 'line': {'width': 1, 'color': 'orange'}
		},
		mode='lines',
		name='Counts [30s]',

	))
	return 	{
			'data': traces,
			'layout': go.Layout(
				# xaxis={'title': 'Time'},
				yaxis={'title': 'Dose [muSv/hr]', 'range': [lim_dose_min, lim_dose_max], 'side': "left", 'titlefont': {'color': "orange"}},
				yaxis2={'title': 'Neutron yield', 'range': [lim_yield_min, lim_yield_max], 'exponentformat':'e', "overlaying": "y", 'side': "right", 'titlefont': {'color': "blue"}},

				height=200,  # px
				showlegend=False,
				margin=dict(t=10, b=15, l=50, r=50),
				hovermode='closest'
			)
		}


# mw power graph
@app.callback(
	Output("sensor_readout_graph_mw_power_readout", "figure"),
	[Input("live_mw_data_readout", "data")],
	[State('experiment_control_data_readout', 'data')]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_mw_power(live_mw_data, experiment_control_data):

	# y limits for the graph
	# experiment_control_data = pd.read_json(experiment_control_data, orient='split')
	# lim_hv_max = float(experiment_control_data['hv_HV_plot_max'].values[0])
	# lim_hv_min = float(experiment_control_data['hv_HV_plot_min'].values[0])


	# print(state_dic)
	traces = []

	try:
		df = pd.read_json(live_mw_data, orient='split')
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

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='MW power',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='MW power',

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


# mw freq graph
@app.callback(
	Output("readout_graph_mw_freq_readout", "figure"),
	[Input("live_mw_data_readout", "data")],
	[State('experiment_control_data_readout', 'data')]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_mw_freq_readout(live_mw_data, experiment_control_data):
	
	traces = []

	try:
		df = pd.read_json(live_mw_data, orient='split')
		# FP
		traces.append(go.Scatter(
			x=df['time'],
			y=df['Freq']/10.0,
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
			y=df['Freq_set']/10.0,
			text='Frequency setpoint [MHz]',
			line=go.scatter.Line(
				color='green',
				width=1.5
			),
			opacity=0.7,

			name='Frequency setpoint [MHz]',
		))


	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='MW frequency',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='MW frequency',

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



# d2flow graph
@app.callback(
	Output("sensor_readout_graph_d2flow_readout", "figure"),
	[Input("live_d2flow_data_readout", "data")],
	[State('experiment_control_data_readout', 'data')]
)
# def plot_graph_data(df, figure, command, start, start_button, PID):
def plot_d2flow(live_d2flow_data, experiment_control_data):

	# y limits for the graph
	# experiment_control_data = pd.read_json(experiment_control_data, orient='split')
	# lim_hv_max = float(experiment_control_data['hv_HV_plot_max'].values[0])
	# lim_hv_min = float(experiment_control_data['hv_HV_plot_min'].values[0])


	# print(state_dic)
	traces = []

	try:
		df = pd.read_json(live_d2flow_data, orient='split')
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

	except:
		traces.append(go.Scatter(
			x=[],
			y=[],
			line=go.scatter.Line(
				color='#42C4F7',
				width=1.0
			),
			text='Flow set [mV]',
			# mode='markers',
			opacity=1,
			marker={
				 'size': 15,
				 'line': {'width': 1, 'color': '#42C4F7'}
			},
			mode='lines',
			name='Flow set [mV]',

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