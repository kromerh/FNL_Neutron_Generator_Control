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
























# Refresh experiment id and date table when clicking anywhere
# Update tag dropdowns when clicking anywhere
@app.callback(
	[
		Output('tbl_live_overview', 'columns'),
		Output('tbl_live_overview', 'data')
	],
	[Input('operation_report_parent', 'n_clicks')])
def click_anywhere(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read number of entries in each table
	count_hv_dose = 0
	qry = "SELECT COUNT(id) as count FROM storage_hv_dose"
	df_hv_dose = pd.read_sql(query, sql_engine)
	if len(df_hv_dose) > 0:
		count_hv_dose = df_hv_dose['count'].values[0]


	count_d2flow = 0
	qry = "SELECT COUNT(id) as count FROM live_d2flow"
	df_d2flow = pd.read_sql(query, sql_engine)
	if len(df_d2flow) > 0:
		count_d2flow = df_d2flow['count'].values[0]


	count_mw = 0
	qry = "SELECT COUNT(id) as count FROM live_mw"
	df_mw = pd.read_sql(query, sql_engine)
	if len(df_mw) > 0:
		count_mw = df_mw['count'].values[0]


	count_pressure = 0
	qry = "SELECT COUNT(id) as count FROM live_pressure"
	df_pressure = pd.read_sql(query, sql_engine)
	if len(df_pressure) > 0:
		count_pressure = df_pressure['count'].values[0]


	count_ref_det = 0
	qry = "SELECT COUNT(id) as count FROM live_ref_det"
	df_ref_det = pd.read_sql(query, sql_engine)
	if len(df_ref_det) > 0:
		count_ref_det = df_ref_det['count'].values[0]


	df = pd.DataFrame()
	df['Sensor'] = ['HV and dose', 'Pressure', 'Microwave', 'D2Flow', 'Reference detectors']
	df['Counts'] = [count_hv_dose, count_pressure, count_mw, count_d2flow, count_ref_det]


	columns = [{"name": i, "id": i} for i in df.columns]
	data = df.to_dict('records')



	return columns, data