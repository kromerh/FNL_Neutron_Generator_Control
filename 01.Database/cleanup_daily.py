# Daily cleanup of the live tables into the storage tables

import pymysql
import sqlalchemy as sql
import pandas as pd
import datetime
import numpy as np
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




# Path to leakage current correction data file
path_LUT_leakage_current = '/home/pi/FNL_Neutron_Generator_Control/03.Dash/01.V1/calibration/LUT_leakage_current.csv'

# Path to LUT for dose rate to neutron output
path_LUT_dose_neutron_output = '/home/pi/FNL_Neutron_Generator_Control/03.Dash/01.V1/calibration/LUT_dose_neutron_output.csv'




def read_table(sql_engine, table):
	"""
	Reads all entries from the table and returns as dataframe
	"""
	query = f"SELECT * FROM {table};"
	df = pd.read_sql(query, sql_engine)
	df['time'] = pd.to_datetime(df['time'].values)

	return df

def leakage_current_correction(path_LUT):

	data_I_leak = pd.read_csv(path_LUT, index_col=0)
	X = data_I_leak['HV_voltage'].values.astype(np.float64)
	Y = data_I_leak['HV_current'].values.astype(np.float64)
	interp_leak = interp1d(X, Y, fill_value='extrapolate')

	return interp_leak

def dose_to_output(path_LUT):

	data_mcnp_LUT = pd.read_csv(path_LUT, index_col=0)
	# position of the sphere is east
	interp_dose = interp1d(data_mcnp_LUT.index, data_mcnp_LUT['E'].values, fill_value='extrapolate')

	return interp_dose


def cleanup_live_hv_dose(sql_engine):
	"""
	Cleans up the live_hv_dose and copies it into the storage table.
	"""
	connection = sql_engine.raw_connection()
	cur = connection.cursor()

	try:
		# load the live_hv_dose
		df = read_table(sql_engine, table='live_hv_dose')

		# calculate dose_rate
		df['dose_rate'] = df['dose_voltage'] * 3000 / 5.5

		# leakage current correction
		interp_leak = leakage_current_correction(path_LUT_leakage_current)
		df['HV_current'] = df['HV_current'] - interp_leak(df['HV_voltage'].values)

		idx = df[df['HV_current'] < 0].index # set negative current values to 0
		df.loc[idx, 'HV_current'] = 0

		# compute neutron output from dose_rate
		interp_dose = dose_to_output(path_LUT_dose_neutron_output)
		df['neutron_output'] = df['dose_rate'].values * (interp_dose(df_hv_dose['HV_voltage'].values) / 100)

		print(df)
		# save to the storage
		# df.to_sql(name=myName, con=connection, if_exists='append', index=False)

		connection.commit()
	except Exception as e:
		connection.rollback()
		modal_body = 'There was an error.'
		raise e


cleanup_live_hv_dose(sql_engine)
