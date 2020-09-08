import pymysql
import sqlalchemy as sql
import pandas as pd

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
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}

sql_engine = sql.create_engine(connect_string)


def insert_user(sql_engine, user_name, user_comment, verbose=False):
	"""
	Insert an entry into the experiment table.
	"""
	if user_name is None:
		modal_text = f"No user name was entered. Abort."
	else:
		if check_user_name_in_db(sql_engine, user_name):
			modal_text = f'Error, user name {user_name} exists already in database. Abort.'
		else:
			table = 'user'
			query = f"""INSERT INTO {table} (name, comment) VALUES (\"{user_name}\", "{user_comment}\");"""
			if verbose: print(query)

			sql_engine.execute(sql.text(query))
			modal_text = f'Saved new user info to database. Query was:\n' + query
	return modal_text

def check_user_name_in_db(sql_engine, user_name):
	"""
	Check if a user name already exists in the user table. If it does, return True, else False
	"""
	query = f"SELECT COUNT(*) as count FROM user WHERE name = \"{user_name}\" "
	count = pd.read_sql(query, sql_engine)['count'].values[0]
	# print(count)
	if count > 0:
		return True
	else:
		return False

def edit_user(sql_engine, user_id, user_name_new, user_comment, verbose=False):
	"""
	Insert an entry into the experiment table.
	"""
	if check_user_name_in_db(sql_engine, user_name_new):
		modal_text = f'Error, user name {user_name_new} exists already in database. Abort.'

		return modal_text

	else:
		table = 'user'
		print(user_name_new)
		print(user_comment)
		# Case 1: both user name and comment
		if (user_name_new is not None) and (user_comment is not None):
			query = f"""UPDATE {table} SET name = \"{user_name_new}\", comment = \"{user_comment}\" WHERE id = \"{user_id}\";"""
			if verbose: print(query)

			sql_engine.execute(sql.text(query))
			modal_text = f'Edited user info in database. Query was:\n' + query

			return modal_text
		# Case 2: only user name
		if (user_name_new is not None):
			query = f"""UPDATE {table} SET name = \"{user_name_new}\" WHERE id = \"{user_id}\";"""
			if verbose: print(query)

			sql_engine.execute(sql.text(query))
			modal_text = f'Edited user info in database. Query was:\n' + query

			return modal_text

		# Case 3: only user comment
		if (user_comment is not None):
			query = f"""UPDATE {table} SET comment = \"{user_comment}\" WHERE id = \"{user_id}\";"""
			if verbose: print(query)

			sql_engine.execute(sql.text(query))
			modal_text = f'Edited user info in database. Query was:\n' + query

			return modal_text

def read_users(sql_engine, table):
	"""
	Reads last limit entries from table table and returns a dataframe
	"""
	query = f"SELECT * FROM {table} ORDER BY id ASC"
	df = pd.read_sql(query, sql_engine)

	return df

# edit experiment text message display that data was saved to db
@app.callback(
    [Output("edit-user-modal", "is_open"), Output("edit-user-modal-body", "children")],
    [Input("edit-user-btn-save", "n_clicks"), Input("edit-user-modal-btn-close", "n_clicks")],
    [State("edit-user-modal", "is_open"), State("edit-user-id", "children"), State("edit-user-name", "value"), State("edit-user-comment", "value"), State("edit-user-name-input", "value")],
)
def toggle_modal_edit_user(n1, n2, is_open, user_id, user_name, user_comment, user_name_new):
	modal_body = 'None'
	if n1 or n2:
		if n1 and not is_open:
			print(f"user_id: {user_id}")
			print(f"user_name_new: {user_name_new}")
			if (user_id not in ['NULL', 'Null', ['NULL'], ['Null']]):
				# case 1: update an existing user name or comment
				modal_body = edit_user(sql_engine, user_id, user_name_new, user_comment, verbose=True)
			else:
				print(' in else')
				modal_body = insert_user(sql_engine, user_name_new, user_comment, verbose=True)
		return not is_open, modal_body
	return is_open, 'None'


# Update user dropdowns when clicking anywhere
@app.callback(
	[Output('edit-user-id', 'options'), Output('edit-user-name', 'options')],
	[Input('parent', 'n_clicks')])
def update_user_dropdown(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read the users as a df
	df_user = read_users(sql_engine, 'user')
	# print(tags)
	# select only the tags
	users = df_user['name'].values

	options_user=[
				{'label': i, 'value': i} for i in users
			]
	user_id = df_user['id'].values

	options_user_id=[
				{'label': i, 'value': i} for i in user_id
			]

	return options_user_id, options_user



# update user id
@app.callback(
	[
	Output('edit-user-id', 'children'),
	Output('edit-user-comment', 'value')
	],
	[
	Input('edit-user-name', 'value'),
	Input("edit-user-btn-save", "n_clicks"),
	Input("edit-user-btn-new", "n_clicks")
	],
	[State('edit-user-state', 'children'),
	State('edit-user-new-clicked', 'children')
	])
def update_user_id(user_name, n_clicks, n_clicks_new, edit_user_state, edit_user_new_clicked):
	# get what triggered the callback
	ctx = dash.callback_context
	trigger  = ctx.triggered[0]['prop_id']

	# cases for different triggers
	# id field
	# print(trigger, n_clicks_new)
	if trigger == 'edit-user-name.value':
		if edit_user_state == None:
			if len(user_name) > 0:
				df = read_users(sql_engine, 'user')
				df = df[df['name'] == user_name]
				user_id = df['id'].values[0]
				user_comment = df['comment'].values[0]

				return user_id, user_comment
			else:
				df = read_users(sql_engine, 'user')
				new_user_id = max(df['id'].values) + 1
				return "Null", ''
		else:
			raise dash.exceptions.PreventUpdate
	# new user button clicked
	if trigger == 'edit-user-btn-new.n_clicks':

		df = read_users(sql_engine, 'user')
		new_user_id = max(df['id'].values) + 1
		return new_user_id, ''

	if trigger == 'edit-user-btn-save.n_clicks':
		return 'Null', ''
	print(trigger)
	# button
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	if n_clicks_new is None:
		raise dash.exceptions.PreventUpdate


# update user name
@app.callback(
	[
	Output('edit-user-name', 'value'),
	Output('edit-user-state', 'children'),
	Output('edit-user-name-input', 'value')
	],
	[
	Input("edit-user-btn-save", "n_clicks"),
	Input("edit-user-btn-new", "n_clicks")
	],
	[State('edit-user-state', 'children')])
def update_user_name(n_clicks, n_clicks_new, edit_user_state):
	ctx = dash.callback_context
	trigger  = ctx.triggered[0]['prop_id']

	if trigger == 'edit-user-btn-new.n_clicks':
		return '', edit_user_state, ''

	if trigger == 'edit-user-btn-save.n_clicks':
		return '', edit_user_state, ''

	if n_clicks_new is None:
		raise dash.exceptions.PreventUpdate
	# else:
	# 	return '', edit_user_state
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate


# # Update the stored user input mask information whenever a value is changed
# @app.callback(
# 	Output('edit-user-store', 'children'),
# 	[
# 	Input('edit-user-id', 'value'),
# 	Input('edit-user-name', 'value'),
# 	Input('edit-user-name-input', 'value'),
# 	Input('edit-user-comment', 'value')
# 	])
# def update_user_store(user_id, user_name, user_new_name, user_comment):
# 	user_store = pd.DataFrame({'user_id': [0], 'user_name': [0], 'user_new_name': [0], 'user_comment': [0]})

# 	# get what triggered the callback
# 	ctx = dash.callback_context
# 	trigger  = ctx.triggered[0]['prop_id']

# 	# cases for different triggers
# 	# id field
# 	if trigger == 'edit-user-id.value':
# 		# load name and comment
# 		df = read_users(sql_engine, 'user')
# 		df = df[df['id'] == user_id]
# 		user_name = df['name'].values[0]
# 		user_comment = df['comment'].values[0]

# 	elif trigger == 'edit-user-name.value':
# 		# load id and comment
# 		df = read_users(sql_engine, 'user')
# 		df = df[df['name'] == user_name]
# 		user_id = df['id'].values[0]
# 		user_comment = df['comment'].values[0]

# 	elif trigger == 'edit-user-name-input.value':
# 		# only update the store
# 		pass

# 	elif trigger == 'edit-user-name-input.value':
# 		# only update the store
# 		pass

# 	print(trigger)

# 	user_store['user_id'] = user_id
# 	user_store['user_name'] = user_name
# 	user_store['user_comment'] = user_comment
# 	user_store['user_new_name'] = user_new_name

# 	print(user_store)
# 	user_store = user_store.to_json(date_format='iso', orient='split')

# 	return user_store

