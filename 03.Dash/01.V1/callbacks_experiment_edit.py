import pymysql
import sqlalchemy as sql
import pandas as pd
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app

app.scripts.config.serve_locally=True

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



def read_experiments(sql_engine, table, limit=1000):
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


def edit_users(sql_engine, cur, modal_body, experiment_id, users):
	"""
	Checks if the current users for this expeirment in the expeirment_users table is the same as for the users selected.
	If not, it will delete the entry in the experiment_users table and replace the entry with the respective one.
	"""
	# get the current users
	query = f"""SELECT \
					experiment_users.user_id, \
					user.name as user_name
				FROM experiment_users \
				INNER JOIN user \
					ON experiment_users.user_id = user.id
				WHERE experiment_users.experiment_id=\"{experiment_id}\";"""
	df_users = pd.read_sql(query, sql_engine)

	# if the users are the same, do nothing
	users_in_db = df_users['user_name'].values.tolist()
	is_same = True
	if len(users_in_db) != len(users):
		is_same = False
	else:
		for user in users_in_db:
			if user not in users:
				is_same = False

	# if there is a new user, change the whole entry in the experiment_users table
	if not is_same:
		# drop all from the table
		query = f"""DELETE FROM experiment_users WHERE experiment_id=\"{experiment_id}\";"""
		cur.execute(query)

		modal_body.append(f'Changed user(s) to the experiment with id {experiment_id}: ')
		# repopulate with new users for that experiment
		for user_name in users:
			# get the id to that name
			# print(user_name)
			query = f"SELECT * FROM user WHERE name =\"{user_name}\";"
			df = pd.read_sql(query, sql_engine)

			user_id = df['id'].values[0]
			query = f"""INSERT INTO experiment_users (experiment_id, user_id) VALUES ((SELECT experiment.id FROM experiment ORDER BY id DESC LIMIT 1), "{user_id}\");"""
			cur.execute(query)
			modal_body.append(f'{user_name}, ')
		modal_body[-1] = modal_body[-1].replace(',','.')
		modal_body.append('\n')
	else:
		modal_body.append('No user change detected.\n')

	return modal_body



def edit_tags(sql_engine, cur, modal_body, experiment_id, tags):
	"""
	Checks if the current tags for this experiment in the experiment_tags table is the same as for the tags selected.
	If not, it will delete the entry in the experiment_tags table and replace the entry with the respective one.
	"""
	# get the current tags
	query = f"""SELECT \
					experiment_tags.tag_id, \
					tag.tag_name as tag_name
				FROM experiment_tags \
				INNER JOIN tag \
					ON experiment_tags.tag_id = tag.id
				WHERE experiment_tags.experiment_id=\"{experiment_id}\";"""
	df_tags = pd.read_sql(query, sql_engine)

	# if the tags are the same, do nothing
	tags_in_db = df_tags['tag_name'].values.tolist()
	is_same = True
	if len(tags_in_db) != len(tags):
		is_same = False
	else:
		for tag in tags_in_db:
			if tag not in tags:
				is_same = False

	# if there is a new tag, change the whole entry in the experiment_tags table
	if not is_same:
		# drop all from the table
		query = f"""DELETE FROM experiment_tags WHERE experiment_id=\"{experiment_id}\";"""
		cur.execute(query)

		modal_body.append(f'Changed tag(s) to the experiment with id {experiment_id}: ')
		# repopulate with new users for that experiment
		for tag_name in tags:
			# get the id to that tag
			query = f"SELECT * FROM tag WHERE tag_name =\"{tag_name}\";"
			df = pd.read_sql(query, sql_engine)

			tag_id = df['id'].values[0]
			query = f"""INSERT INTO experiment_tags (experiment_id, tag_id) VALUES ((SELECT experiment.id FROM experiment ORDER BY id DESC LIMIT 1), "{tag_id}\");"""
			cur.execute(query)
			modal_body.append(f'{tag_name}, ')
		modal_body[-1] = modal_body[-1].replace(',','.')
		modal_body.append('\n')
	else:
		modal_body.append('No tag change detected.\n')

	return modal_body

def save_experiment(sql_engine, experiment_id, users, tags, comment):
	modal_body = []

	# check that user and tags are there
	if (len(users) > 0) and (len(tags) > 0):
		connection = sql_engine.raw_connection()
		cur = connection.cursor()

		try:
			# edit the comment
			query = f"""UPDATE experiment SET comment=\"{comment}\" WHERE experiment.id=\"{experiment_id}\";"""
			cur.execute(query)
			modal_body.append('Changed comment.\n')


			# edit the users
			modal_body = edit_users(sql_engine, cur, modal_body, experiment_id, users)


			# edit the tags
			modal_body = edit_tags(sql_engine, cur, modal_body, experiment_id, tags)

			connection.commit()
		except Exception as e:
			connection.rollback()
			modal_body = 'There was an error.'
			raise e


	else:
		modal_body = 'No user or no tags entered. Nothing will be saved. Abort.'

	modal_body = "".join(modal_body)


	return modal_body



# Update experiment date and id dropdowns when clicking anywhere
@app.callback(
	[
	Output('edit-experiment-date', 'options'),
	Output('edit-experiment-id', 'options'),
	Output('edit-experiment-user', 'options'),
	Output('edit-experiment-tag', 'options')
	],
	[Input('parent', 'n_clicks'), Input('edit-experiment-date', 'value')])
def update_experiment_edit_dropdown(n_clicks_anywhere, date_value):
	ctx = dash.callback_context
	trigger  = ctx.triggered[0]['prop_id']

	# get tag options
	# read the tags as a df
	tags = read_tags(sql_engine, 'tag')
	# print(tags)
	# select only the tags
	tags = tags['tag_name'].values
	# print(tags)
	options_tags=[
				{'label': i, 'value': i} for i in tags
			]
	# get user options

	# read the users as a df
	users = read_users(sql_engine, 'user')
	# print(tags)
	# select only the tags
	users = users['name'].values

	options_users=[
				{'label': i, 'value': i} for i in users
			]


	# print(f"trigger: {trigger}")
	# print(f'date_value: {date_value}')
	# if triggered by a click anywhere, update both the date and id dropdown
	if trigger == 'parent.n_clicks':
		# if no date selected
		if date_value == None:
			# print(f"date_value IS None, it is {date_value}")

			# connect to database and read all
			df = read_experiments(sql_engine, 'experiment')
			dates = list(df['date'].dt.strftime('%Y-%m-%d').unique()) # select only the dates as string

			ids = df['id'].values
			# print(dates, ids)
			options_dates=[
					{'label': i, 'value': i} for i in dates
				]
			options_ids=[
					{'label': i, 'value': i} for i in ids
				]


			return options_dates, options_ids, options_users, options_tags

		else:
			# print(f"date_value is not None, it is {date_value}")
			# return only for that date the ids
			# connect to database and read all
			df = read_experiments(sql_engine, 'experiment')
			dates = list(df['date'].dt.strftime('%Y-%m-%d').unique()) # select only the dates as string

			# read ids only for that date
			query = f"SELECT * FROM experiment WHERE date BETWEEN \"{date_value} 00:00:00\" AND \"{date_value} 23:59:59\" ORDER BY id DESC;"
			df = pd.read_sql(query, sql_engine)
			# print(df)
			ids = df['id'].values



			options_dates=[
					{'label': i, 'value': i} for i in dates
				]
			options_ids=[
					{'label': i, 'value': i} for i in ids
				]

			return options_dates, options_ids, options_users, options_tags

	if (n_clicks_anywhere is None) or (date_value is None):
		raise dash.exceptions.PreventUpdate

	else:
		# connect to database and read all
		df = read_experiments(sql_engine, 'experiment')
		dates = list(df['date'].dt.strftime('%Y-%m-%d').unique()) # select only the dates as string

		# read ids only for that date
		query = f"SELECT * FROM experiment WHERE date BETWEEN \"{date_value} 00:00:00\" AND \"{date_value} 23:59:59\" ORDER BY id DESC;"
		df = pd.read_sql(query, sql_engine)

		ids = df['id'].values


		options_dates=[
				{'label': i, 'value': i} for i in dates
			]
		options_ids=[
				{'label': i, 'value': i} for i in ids
			]

		return options_dates, options_ids, options_users, options_tags


# Load experiment users, tags, and comments
@app.callback(
	[
	Output('edit-experiment-user', 'value'),
	Output('edit-experiment-tag', 'value'),
	Output('edit-experiment-comment', 'value')
	],
	[Input('edit-experiment-id', 'value')])
def update_experiment_load_values(id_value):
	# load the content of that experiment id from the database
	if id_value is None:
		raise dash.exceptions.PreventUpdate

	query = f"""SELECT \
	experiment.id as experiment_id, \
	experiment.comment as comment, \
	experiment_tags.tag_id as tag_id, \
	tag.tag_name as tag_name, \
	user.name as user_name \
	FROM experiment \
	LEFT JOIN experiment_tags \
	ON experiment.id = experiment_tags.experiment_id \
	LEFT JOIN experiment_users \
	ON experiment.id = experiment_users.experiment_id \
	LEFT JOIN tag \
	ON tag_id = tag.id \
	LEFT JOIN user \
	ON user_id = user.id \
	WHERE experiment.id = \"{id_value}\";"""
	# query = re.sub(r'[\t]', '', query)

	# print(query)
	df = pd.read_sql(query, sql_engine)

	# get the comment
	comment = df['comment'].values[0]

	# get the users
	users = df['user_name'].unique().tolist()
	if users[0] is None:
		users = ''

	# get the tags
	tags = df['tag_name'].unique().tolist()
	if tags[0] is None:
		tags = ''

	# return user, tag, comment
	# print(users, tags, comment)
	return users, tags, comment




# edit text message display that data was saved to db
@app.callback(
	[Output("edit-experiment-modal", "is_open"), Output("edit-experiment-modal-body", "children")],
	[Input("edit-experiment-btn-save", "n_clicks"),
	Input("edit-experiment-modal-btn-close", "n_clicks")],
	[State("edit-experiment-modal", "is_open"),
	State('edit-experiment-id', 'value'),
	State('edit-experiment-user', 'value'),
	State('edit-experiment-tag', 'value'),
	State('edit-experiment-comment', 'value')],
)
def toggle_modal_edit_experiment(n1, n2, is_open, experiment_id, experiment_user, experiment_tag, experiment_comment):
	modal_body = 'None'
	if n1 or n2:
		if n1 and not is_open:

			# print(f"experiment_id: {experiment_id}")
			# print(f"experiment_user: {experiment_user}")
			# print(f"experiment_tag: {experiment_tag}")
			# print(f"experiment_comment: {experiment_comment}")

			modal_body = save_experiment(sql_engine, experiment_id, experiment_user, experiment_tag, experiment_comment)
			# print(modal_body)
		return not is_open, modal_body
	return is_open, 'None'






