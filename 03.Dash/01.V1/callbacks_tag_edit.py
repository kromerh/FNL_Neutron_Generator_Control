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

def read_tags(sql_engine, table):
	"""
	Reads last limit entries from table table and returns a dataframe
	"""
	query = f"SELECT * FROM {table} ORDER BY id ASC"
	df = pd.read_sql(query, sql_engine)

	return df


def check_tag_name_in_db(sql_engine, tag_name):
	"""
	Check if a tag name already exists in the user table. If it does, return True, else False
	"""
	query = f"SELECT COUNT(*) as count FROM tag WHERE tag_name = \"{tag_name}\" "
	count = pd.read_sql(query, sql_engine)['count'].values[0]
	print(count)
	if count > 0:
		return True
	else:
		return False



def edit_tag(sql_engine, tag_id, tag_name_new, verbose=False):
	"""
	Edit an entry into the tag table.
	"""
	if check_tag_name_in_db(sql_engine, tag_name_new):
		modal_text = f'Error, tag name {tag_name_new} exists already in database. Abort.'

		return modal_text

	else:
		table = 'tag'
		print(tag_name_new)

		if (tag_name_new is not None) :
			query = f"""UPDATE {table} SET tag_name = \"{tag_name_new}\" WHERE id = \"{tag_id}\";"""
			if verbose: print(query)

			sql_engine.execute(sql.text(query))
			modal_text = f'Edited tag info in database. Query was:\n' + query

			return modal_text
		else:
			modal_text = f'Error, no tag name ({tag_name_new}) found. Abort.'

			return modal_text



def insert_tag(sql_engine, tag_name, verbose=False):
	"""
	Insert an entry into the tag table.
	"""
	if tag_name is None:
		modal_text = f"No tag name was entered. Abort."
	else:
		if check_tag_name_in_db(sql_engine, tag_name):
			modal_text = f'Error, tag name {tag_name} exists already in database. Abort.'
		else:
			table = 'tag'
			query = f"""INSERT INTO {table} (tag_name) VALUES (\"{tag_name}\");"""
			if verbose: print(query)

			sql_engine.execute(sql.text(query))
			modal_text = f'Saved new tag to database. Query was:\n' + query
	return modal_text








# edit experiment text message display that data was saved to db
@app.callback(
	[Output("edit-tag-modal", "is_open"), Output("edit-tag-modal-body", "children")],
    [Input("edit-tag-btn-save", "n_clicks"), Input("edit-tag-modal-btn-close", "n_clicks")],
    [State("edit-tag-modal", "is_open"), State("edit-tag-id", "children"), State("edit-tag-name-input", "value")],
)
def toggle_modal_edit_tag(n1, n2, is_open, tag_id, tag_new_name):
	modal_body = 'None'
	if n1 or n2:
		if n1 and not is_open:
			# print(f"tag_id: {tag_id}")
			# print(f"tag_new_name: {tag_new_name}")
			if (tag_id not in ['NULL', 'Null', ['NULL'], ['Null']]):
				# case 1: update an existing user name or comment
				modal_body = edit_tag(sql_engine, tag_id, tag_new_name, verbose=True)
			else:
				# print(' in else')
				modal_body = insert_tag(sql_engine, tag_new_name, verbose=True)
		return not is_open, modal_body
	return is_open, 'None'




# Update user dropdowns when clicking anywhere
@app.callback(
	Output('edit-tag-name', 'options'),
	[Input('parent', 'n_clicks')])
def update_tag_dropdown(n_clicks):
	if n_clicks is None:
		raise dash.exceptions.PreventUpdate

	# read the users as a df
	df = read_tags(sql_engine, 'tag')
	# print(tags)
	# select only the tags
	tags = df['tag_name'].values

	options_tags =[
				{'label': i, 'value': i} for i in tags
			]

	return options_tags




# update tag id
@app.callback(
	Output('edit-tag-id', 'children')
	,
	[
	Input("edit-tag-btn-save", "n_clicks"),
	Input("edit-tag-btn-new", "n_clicks"),
	Input('edit-tag-name', 'value')
	])
def update_tag_id(n_clicks_save, n_clicks_new,tag_name):
	# get what triggered the callback
	ctx = dash.callback_context
	trigger  = ctx.triggered[0]['prop_id']
	# print(f'update_tag_id {trigger}')
	# cases for different triggers
	if trigger == 'edit-tag-name.value':
		if len(tag_name) > 0:
			df = read_tags(sql_engine, 'tag')
			df = df[df['tag_name'] == tag_name]
			tag_id = df['id'].values[0]

			return tag_id
		else:
			return 'NULL'
			raise dash.exceptions.PreventUpdate

	if trigger == 'edit-tag-btn-save.n_clicks':

		return 'NULL'
	if trigger == 'edit-tag-btn-new.n_clicks':

		return 'NULL'

	# button
	if n_clicks_save is None:
		raise dash.exceptions.PreventUpdate

	if n_clicks_new is None:
		raise dash.exceptions.PreventUpdate

	raise dash.exceptions.PreventUpdate

# update tag name and input
@app.callback(
	[Output('edit-tag-name', 'value'),
	Output('edit-tag-name-input', 'value')]
	,
	[
	Input("edit-tag-btn-save", "n_clicks"),
	Input("edit-tag-btn-new", "n_clicks")
	])
def update_tag_name(n_clicks_save, n_clicks_new):
	ctx = dash.callback_context
	trigger  = ctx.triggered[0]['prop_id']
	# print(f'update_tag_name {trigger}')
	if trigger == 'edit-tag-btn-new.n_clicks':
		# print('test')
		return '', ''

	if trigger == 'edit-tag-btn-save.n_clicks':
		return '', ''
	# button
	if n_clicks_save is None:
		raise dash.exceptions.PreventUpdate

	if n_clicks_new is None:
		raise dash.exceptions.PreventUpdate

	raise dash.exceptions.PreventUpdate
