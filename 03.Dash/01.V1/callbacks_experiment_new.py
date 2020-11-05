import pymysql
import sqlalchemy as sql
import pandas as pd
import datetime
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app
import os


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


def insert_experiment(sql_engine, date, user_names, user_tags, comment, verbose=False):
	"""
	Insert an entry into the experiment table.
	"""
	modal_text = []
	table = 'experiment'
	query = f"""INSERT INTO {table} (date, comment) VALUES (\"{date}\", "{comment}\");"""
	if verbose: print(query)
	sql_engine.execute(sql.text(query))
	modal_text.append(f'Saved experiment info to database. Query was:\n' + query)

	# get latest experiment id
	# update experiment users
	for user_name in user_names:
		# get the id to that name

		query = f"SELECT * FROM user WHERE name =\"{user_name}\";"
		df = pd.read_sql(query, sql_engine)

		user_id = df['id'].values[0]
		query = f"""INSERT INTO experiment_users (experiment_id, user_id) VALUES ((SELECT experiment.id FROM experiment ORDER BY id DESC LIMIT 1), "{user_id}\");"""
		modal_text.append(query+'\n')

		if verbose: print(query)
		sql_engine.execute(sql.text(query))

	for user_tag in user_tags:

		query = f"SELECT * FROM tag WHERE tag_name =\"{user_tag}\";"
		df = pd.read_sql(query, sql_engine)

		tag_id = df['id'].values[0]
		query = f"""INSERT INTO experiment_tags (experiment_id, tag_id) VALUES ((SELECT experiment.id FROM experiment ORDER BY id DESC LIMIT 1), "{tag_id}\");"""
		modal_text.append(query+'\n')

		if verbose: print(query)
		sql_engine.execute(sql.text(query))

	modal_text = "".join(modal_text)

	return modal_text

def read_experiments(sql_engine, table, limit=3):
	"""
	Reads last limit entries from table table and returns a dataframe
	"""
	query = f"SELECT * FROM {table} ORDER BY id DESC LIMIT {limit}"
	df = pd.read_sql(query, sql_engine)

	return df


def read_tags(sql_engine, table):
	"""
	Reads last limit entries from table table and returns a dataframe
	"""
	query = f"SELECT * FROM {table} ORDER BY id ASC"
	df = pd.read_sql(query, sql_engine)

	return df


def read_users(sql_engine, table):
	"""
	Reads last limit entries from table table and returns a dataframe
	"""
	query = f"SELECT * FROM {table} ORDER BY id ASC"
	df = pd.read_sql(query, sql_engine)

	return df




# Click on button SAVE
@app.callback(
	[Output("new-experiment-modal", "is_open"), Output("new-experiment-modal-body", "children")],
	[Input("new-experiment-btn-save", "n_clicks"), Input("new-experiment-modal-btn-close", "n_clicks")],
	[State("new-experiment-modal", "is_open"), State("new-experiment-user", "value"), State("new-experiment-tag", "value"), State("new-experiment-date", "children"), State("new-experiment-comment", "value")],
)
def toggle_modal_new_experiment(n1, n2, is_open, user_names, user_tags, date, comment):
	modal_body = 'none'
	if n1 or n2:
		if n1 and not is_open:
			if (len(user_names) > 0) and (len(user_tags) > 0):
				modal_body = insert_experiment(sql_engine, date, user_names, user_tags, comment, verbose=True)
			else:
				modal_body = 'No user or no tags entered. Nothing will be saved. Abort.'
		return not is_open, modal_body
	return is_open, 'None'


# Click on button NEW EXPERIMENT
@app.callback([Output('new-experiment-date', 'children'),
				Output('new-experiment-id', 'children'),
				Output('new-experiment-tag', 'value'),
				Output('new-experiment-user', 'value'),
				Output('new-experiment-comment', 'value')
				],
			  [Input('new-experiment-btn-new', 'n_clicks'),Input("new-experiment-btn-save", "n_clicks")],
			  [State('new-experiment-btn-new', 'n_clicks_timestamp')])
def new_experiment(n_clicks, n_clicks_save, n_clicks_timestamp):
	ctx = dash.callback_context
	trigger  = ctx.triggered[0]['prop_id']
	print(trigger)
	if trigger == 'new-experiment-btn-new.n_clicks':
		# get current time
		date = datetime.datetime.now().replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

		# get latest experiment id in database
		experiment_id = read_experiments(sql_engine, 'experiment', limit=3)['id'].values[0] # latest one

		# increment it by one
		experiment_id += 1

		experiment_tag_options = ''
		experiment_user_options = ''
		experiment_comment_textarea = ''
		return date, experiment_id, experiment_tag_options, experiment_user_options, experiment_comment_textarea
	elif trigger == 'new-experiment-btn-save.n_clicks':
		date = 'NULL'
		experiment_id = 'NULL'
		experiment_tag_options = ''
		experiment_user_options = ''
		experiment_comment_textarea = ''
		return date, experiment_id, experiment_tag_options, experiment_user_options, experiment_comment_textarea
	if (n_clicks is None) or (n_clicks_save is None):
		raise dash.exceptions.PreventUpdate


# Update tag dropdowns when clicking anywhere
@app.callback(
	[Output('new-experiment-tag', 'options'), Output('new-experiment-user', 'options')],
	[Input('parent', 'n_clicks')])
def update_tag_dropdown(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read the tags as a df
	tags = read_tags(sql_engine, 'tag')
	# print(tags)
	# select only the tags
	tags = tags['tag_name'].values
	# print(tags)
	options_tag=[
				{'label': i, 'value': i} for i in tags
			]
	# read the users as a df
	users = read_users(sql_engine, 'user')
	# print(tags)
	# select only the tags
	users = users['name'].values

	options_user=[
				{'label': i, 'value': i} for i in users
			]

	return options_tag, options_user