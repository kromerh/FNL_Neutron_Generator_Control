# Daily cleanup of the live tables into the storage tables

import pymysql
import sqlalchemy as sql
import pandas as pd
import datetime




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



print(user, pw, host, db)



# hv_dose
def read_hv_dose(sql_engine):
	"""
	Reads all entries from the hv_dose table and returns as dataframe
	"""
	query = f"SELECT * FROM live_hv_dose;"
	df = pd.read_sql(query, sql_engine)
	df['date'] = pd.to_datetime(df['date'].values)

	return df