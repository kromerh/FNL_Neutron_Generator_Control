import re
import sys
import sqlalchemy as sql
import datetime
import time
from time import sleep
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np

# Settings for the simulator
# path
PATH_CREDENTIALS = '~/credentials.pw'

# readout frequency
FREQUENCY = 1 # sleep time in second


VERBOSE = True


# read password and user to database

credentials = pd.read_csv(PATH_CREDENTIALS, header=0)

user = str(credentials['username'].values[0])
pw = str(credentials['password'].values[0])
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}

sql_engine = sql.create_engine(connect_string)




def get_experiment_id(sql_engine, verbose=False):
	query = f"SELECT * FROM experiment_control;"
	df = pd.read_sql(query, sql_engine)

	experiment_id = df['experiment_id'].values[0]


	if verbose: print(f"Experiment id is {experiment_id}")

	return experiment_id





def saveDB(experiment_id, s1, s2, s3, verbose=False):
	# Create a Cursor object to execute queries.
	query = f"""INSERT INTO live_leak (experiment_id, s1, s2, s3) VALUES (\"{experiment_id}\", {s1}, {s2}, {s3});"""
	sql_engine.execute(sql.text(query))

	if verbose: print(query)


while True:
	try:

		experiment_id= get_experiment_id(sql_engine, VERBOSE)
		# get three random numbers
		r = np.random.rand(3,1)
		mask = r > 0.5
		s = (mask * 1).reshape(1, -1)[0]
		s1, s2, s3 = s
		saveDB(experiment_id, s1, s2, s3, VERBOSE)

		sleep(FREQUENCY)
	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		sys.exit(1)


