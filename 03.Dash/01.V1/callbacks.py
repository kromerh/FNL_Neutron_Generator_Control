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

# read password and user to database
credentials_file = r'/Users/hkromer/02_PhD/01.github/FNL_Neutron_Generator_Control/credentials.pw'

credentials = pd.read_csv(credentials_file, header=0)
user = credentials['username'].values[0]
pw = credentials['password'].values[0]
host="localhost"  # your host
user=user # username
passwd=pw  # password
db="wohnung" # name of the database
connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)

def load_interessenten(sql_engine):
    """
    Reads all the interessenten
    """
    query = f"SELECT * FROM user"
    df = pd.read_sql(query, sql_engine)

    return df


# Refresh interessenten when clicking anywhere

@app.callback(
		Output('drpdwn_name', 'options')
	,
	[Input('parent', 'n_clicks')])
def click_anywhere(n_clicks):
	print(1)
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read the experiment id table in the database
	df = load_interessenten(sql_engine)

	vn = df['vorname'].values
	nn = df['nachname'].values

	# what to display as the dropdown options
	options=[
				{'label': f'{vn[ii]} {nn[ii]}', 'value': f'{vn[ii]} {nn[ii]}'} for i in range(0,len(vn))
			]
	print(vn)
	return options