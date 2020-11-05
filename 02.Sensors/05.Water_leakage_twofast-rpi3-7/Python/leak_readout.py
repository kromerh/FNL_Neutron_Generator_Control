import serial
import serial.tools.list_ports
import re
import sys
import pymysql
import re
import sys
import sqlalchemy as sql
import datetime
import time
from time import sleep
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np

PATH_CREDENTIALS = r'/home/pi/credentials.pw' # on the RPi3
ARDUINO_PORT = '/dev/ttyACM0'
VERBOSE = True




# connect to database
credentials = pd.read_csv(PATH_CREDENTIALS, header=0)

user = credentials['username'].values[0]
pw = credentials['password'].values[0]
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)

# connect to arduino
serialArduino = serial.Serial(port=ARDUINO_PORT, baudrate=9600)


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

def fun_read_serial_ports():
	return list(serial.tools.list_ports.comports())

def pi_flush(serial_port):
	serialArduino = serial.Serial(port=serial_port, baudrate=9600)
	serialArduino.flushInput()  #flush input buffer, discarding all its contents
	serialArduino.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer

def pi_read(serial_port):
	serialArduino = serial.Serial(port=serial_port, baudrate=9600)
	while (serialArduino.inWaiting() == 0):  # wait for incoming data
		pass
	valueRead = serialArduino.readline()
	# print(valueRead)
	try:
		valueRead = (valueRead.decode('utf-8')).strip()
		serialArduino.flushInput()  #flush input buffer, discarding all its contents
		serialArduino.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
	   # print(valueRead)
	except UnicodeDecodeError:
		valueRead = '-1'
	return valueRead

while True:
	try:


		experiment_id = get_experiment_id(sql_engine, VERBOSE)

		# read arduino
		ardRead = pi_read(ARDUINO_PORT)
		s = ardRead.rstrip().split()
		now = datetime.datetime.now()
		now = now.strftime(format='%Y-%m-%d %H:%M:%S')
		print(' ')
		if len(s) == 3:  # V1 V2 extractionOn
			s1 = float(s[0])
			s2 = float(s[1])
			s3 = float(s[2])
			sys.stdout.write('Reading leak sensors 1, 2, 3 ...')
			sys.stdout.write(f'{now}, {voltage_IS}, {voltage_VC}')
			saveDB(experiment_id, s1, s2, s3, VERBOSE)
		sleep(0.1)

	except KeyboardInterrupt:
		print('Ctrl + C. Exiting. Flushing serial connection.')
		pi_flush(ARDUINO_PORT)
		sys.exit(1)
	finally:
		pi_flush(ARDUINO_PORT)
	saveDB(experiment_id, s1, s2, s3, VERBOSE)

