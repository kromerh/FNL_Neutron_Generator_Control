import serial
import serial.tools.list_ports
import re
import sys
import pymysql
from time import sleep
import pandas as pd
import numpy as np
import sqlalchemy as sql
import datetime
import time
import pandas as pd
import getopt


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



def pi_flush(serial_port):
    serialArduino = serial.Serial(port=serial_port, baudrate=9600)
    serialArduino.flushInput()  #flush input buffer, discarding all its contents
    serialArduino.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer


def get_flow_meter_control_values(sql_engine, verbose=False):

	query = "SELECT experiment_id, d2flow_set FROM experiment_control"
	df = pd.read_sql(query, sql_engine)

	setpoint_voltage = df['d2flow_set'].values[0]
	experiment_id = df['experiment_id'].values[0]

	if verbose: sys.stdout.write(f"Experiment id: {experiment_id}, Setpoint: {setpoint_voltage} " )

	return experiment_id, setpoint_voltage

def send_voltage_flowmeter(serialArduino, setpoint_voltage):
	sys.stdout.write(f"Sending voltage: {setpoint_voltage} to Arduino " )

	# send
	setpoint_voltage = str(setpoint_voltage)
	serialArduino.write(setpoint_voltage.encode()) # Convert the decimal number to ASCII then send it to the Arduino


def read_live():
	while True:
		try:
			experiment_id, setpoint_voltage = get_flow_meter_control_values(sql_engine, VERBOSE)
			print(' ')

			# send voltage to arduino
			send_voltage_flowmeter(serialArduino, setpoint_voltage)
			sleep(0.5) # Delay

			# read setpoint from arduino
			valueRead = serialArduino.readline(500) # b'V_1 1.30, 4.20, V_out 215.04\r\n'
			#     sys.stdout.write('Reading hv and dose voltages  ...')
			#     sys.stdout.write(f'{now}, HV: {HV_voltage}, I: {HV_current}, dose: {dose_voltage} ')
			print('Raw reading from Arduino :' + str(valueRead)) # Read the newest output from the Arduino
			voltageStr = str(valueRead).split(',')

			voltageStr = voltageStr[0]

	# 		t = re.findall(r'V_1 (.+)', voltageStr)

	# 		if len(t) > 0:
	# 			voltage = t[0]
	# 			# print(voltage)
	# 			saveFlowMeterVoltageToDB(voltage, setpoint_voltage) # save into DB



			# # read arduino
			# ardRead = pi_read(ARDUINO_PORT)
			# s = ardRead.rstrip().split()
			# now = datetime.datetime.now()
			# now = now.strftime(format='%Y-%m-%d %H:%M:%S')
			# print(' ')
			# if len(s) == 5:
			#     dose_voltage = float(s[2])
			#     HV_current = float(s[3])  # 0 - 2 mA
			#     HV_voltage = float(s[4])  # -(0-150) kV
			#     # HV_voltage = float(interp_HV_voltage(HV_voltage))
			#     # HV_current = float(interp_HV_current(HV_current))
			#     # print(HV_voltage)

			#     voltage_IS = float(s[0])
			#     voltage_VC = float(s[1])
			#     sys.stdout.write('Reading hv and dose voltages  ...')
			#     sys.stdout.write(f'{now}, HV: {HV_voltage}, I: {HV_current}, dose: {dose_voltage} ')
			#     saveDB(experiment_id, HV_voltage, HV_current, dose_voltage, VERBOSE)
			sleep(0.1)

		except KeyboardInterrupt:
			print('Ctrl + C. Exiting. Flushing serial connection.')
			pi_flush(ARDUINO_PORT)
			sys.exit(1)
		finally:
			pi_flush(ARDUINO_PORT)



if __name__ == '__main__':
	# Get the arguments from the command-line except the filename
	argv = sys.argv[1:]

	try:
		if len(argv) == 1:
			MODE = argv[0]
			if MODE == '--live':
				read_live()
			else:
				print('Error! usage: d2flow_readout.py --MODE. MODE can only be live')
				sys.exit(2)
		else:
			print('Error! usage: d2flow_readout.py --MODE. MODE can only be live')
			sys.exit(2)

	except getopt.GetoptError:
		# Print something useful
		print('Error! usage: d2flow_readout.py --MODE. MODE can only be live')
		sys.exit(2)











# ser = serial.Serial(arduinoPort, 9600)
# print('Serial connected at ' + str(arduinoPort))
# sleep(1)
# # val = 0.5 # Below 32 everything in ASCII is gibberish
# while True:
# 	try:
# 		# SETPOINT VALUE OF FLOW METER
# 		# read the database for the setpoint value
# 		setpoint_voltage = getFlowMeterControlValues()

# 		# convert
# 		valueSend = str(setpoint_voltage)
# 		# print("Sending value to Arduino " + valueSend)
# 		# send
# 		ser.write(valueSend.encode()) # Convert the decimal number to ASCII then send it to the Arduino

# 		print("Successfully sent to Arduino:" + str(valueSend.encode()))

# 		sleep(0.5) # Delay

# 		# READING OF FLOW METER
# 		valueRead = ser.readline(500) # b'V_1 1.30, 4.20, V_out 215.04\r\n'

# 		print('Raw reading from Arduino :' + str(valueRead)) # Read the newest output from the Arduino
# 		voltageStr = str(valueRead).split(',')

# 		voltageStr = voltageStr[0]



# 		t = re.findall(r'V_1 (.+)', voltageStr)

# 		if len(t) > 0:
# 			voltage = t[0]
# 			# print(voltage)
# 			saveFlowMeterVoltageToDB(voltage, setpoint_voltage) # save into DB

# 		sleep(0.5) # Delay
# 		ser.flushInput()  #flush input buffer, discarding all its contents
# 		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
# 	except KeyboardInterrupt:
# 		print('Ctrl + C. Exiting. Flushing serial connection.')
# 		ser.flushInput()  #flush input buffer, discarding all its contents
# 		ser.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
# 		sys.exit(1)