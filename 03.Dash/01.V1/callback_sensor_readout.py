import pymysql
import sqlalchemy as sql
import pandas as pd
import datetime

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



def read_experiment_id(sql_engine):
	"""
	Reads the experiment_id from the experiment_control table and the corresponding date and returns both
	"""

	query = f"SELECT experiment_id FROM experiment_control;"
	df = pd.read_sql(query, sql_engine)

	experiment_id = df['experiment_id'].values

	query = f"SELECT date FROM experiment WHERE experiment_id = {experiment_id};"
	df = pd.read_sql(query, sql_engine)
	date = df['date'].values[0]

	return experiment_id, date

# Refresh experiment id and date when clicking anywhere
@app.callback(
	[
		Output('P_experiment_id_readout', 'children'),
		Output('P_experiment_date_readout', 'children'),
		],
	[Input('sensor_readout_parent', 'n_clicks')])
def click_anywhere(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read the experiment id table in the database
	experiment_id, date = read_experiment_id(sql_engine)

	return experiment_id, date