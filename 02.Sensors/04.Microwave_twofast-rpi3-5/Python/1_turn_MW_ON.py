from pyModbusTCP.client import ModbusClient
from time import sleep
import sys
import getopt
from time import sleep
import serial
import pandas as pd
import pymysql
import re
import sqlalchemy as sql

# MAC Address of the microwave generator
# MAC Address: 00:80:A3:C2:AB:65 (Lantronix)

# find the ip address of the microwave
# sudo tcpdump -i eth1


PATH_CREDENTIALS = r'/home/pi/credentials.pw' # on the RPi3
VERBOSE = True


# connect to database
credentials = pd.read_csv(PATH_CREDENTIALS, header=0)

user = credentials['username'].values[0]
pw = credentials['password'].values[0]
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)


def saveDB(experiment_id, FP, FP_set, RP, Freq, Freq_set, code, verbose=False):
	# Create a Cursor object to execute queries.
	query = f"""INSERT INTO live_mw (experiment_id, FP, FP_set, RP, Freq, Freq_set, code) VALUES (\"{experiment_id}\", \"{FP}\", \"{FP_set}\", \"{RP}\", \"{Freq}\", \"{Freq_set}\", \"{code}\");"""
	sql_engine.execute(sql.text(query))

	if verbose: sys.stdout.write(query)


def get_experiment_id(sql_engine, verbose=False):
	query = f"SELECT mw_fp_set, mw_freq_set, experiment_id FROM experiment_control;"
	df = pd.read_sql(query, sql_engine)

	experiment_id = df['experiment_id'].values[0]
	mw_fp_set = df['mw_fp_set'].values[0]
	mw_freq_set = df['mw_freq_set'].values[0]

	if verbose: sys.stdout.write(f"Experiment id {experiment_id}, {mw_fp_set}, {mw_freq_set} ")

	return experiment_id, mw_fp_set, mw_freq_set



def live(mw_ip):

	mw_ip = str(mw_ip)



	# sudo
	try:
		# c = ModbusClient(host="169.254.150.42", port=502, auto_open=True, auto_close=True)
		c = ModbusClient(host=mw_ip, port=502, auto_open=True, auto_close=True)
		# c = ModbusClient(host="169.254.240.1", port=502, auto_open=True, auto_close=True)
	except ValueError:
		print("Error with host or port params")



	# bool to store if all the settings are set
	RAMP_SET = False
	RAMP_TIME_SET = False
	FP_SET = False
	RP_SET = False
	MODE_SET = False
	MW_ON = False
	FREQ_SET = False


	def send_heartbeat(ModbusClient):
		# sends MODBUS heart beat
		# c is ModbusClient
		wr = ModbusClient.write_single_register(20, 128) # modbus heartbeat

	def set_start_mode_ramp(ModbusClient):
		# Sets the start mode to ramp
		# c is ModbusClient
		wr = ModbusClient.write_single_register(3,2)
		# print('set_start_mode_ramp:' + str(int(wr)))
		return wr

	def set_start_time(ModbusClient):
		# Sets the start time to 60s
		# c is ModbusClient
		wr = ModbusClient.write_single_register(4,60)
		# print('set_start_time:' + str(int(wr)))
		return wr

	def set_FW_power(ModbusClient, mw_fp_set):
		# Sets the forward power set point to 200 W
		# c is ModbusClient
		# wr = ModbusClient.write_single_register(0,200)
		wr = ModbusClient.write_single_register(0,mw_fp_set)
		# print('set_FW_power:' + str(int(wr)))
		return wr

	def set_RP(ModbusClient):
		# Sets the reflected power set point to 100 W
		# c is ModbusClient
		wr = ModbusClient.write_single_register(1,100)
		# print('set_RP:' + str(int(wr)))
		return wr

	def set_freq(ModbusClient, mw_freq_set):
		# Sets the frequency before the autotuning
		# c is ModbusClient
		wr = ModbusClient.write_single_register(9,mw_freq_set)
		# print('set_freq:' + str(int(wr)))
		return wr

	def set_microwave_mode(ModbusClient):
		# Sets the microwave mode:
		#	autotuning on, reflected power RP limitation, reset faults
		# c is ModbusClient
		bit_addr = 2
		bit_value = 146 # 0 1 0 0 1 0 0 1
		wr = c.write_single_register(bit_addr, bit_value)
		# print('set_microwave_mode:' + str(int(wr)))
		return wr

	def set_microwave_ON(ModbusClient):
		# Sets the microwave mode:
		#	autotuning on, reflected power RP limitation, MW ON, reset faults
		# c is ModbusClient
		bit_addr = 2
		bit_value = 210 # 0 1 0 0 1 0 1 1
		wr = c.write_single_register(bit_addr, bit_value)
		# print('set_microwave_ON:' + str(int(wr)))
		return wr



	def read_fault_present(ModbusClient):
		# reads if fault present
		r0 = c.read_holding_registers(104, 1)
		r1 = c.read_holding_registers(105, 1)

		return [r0[0], r1[0]]

	def read_FP(ModbusClient):
		# reads forward power
		r0 = c.read_holding_registers(102, 1)
		# print('read_FP :')
		# print(r0)
		return r0

	def read_RP(ModbusClient):
		# reads reflected power
		r0 = c.read_holding_registers(103, 1)
		# print('read_RP:')
		# print(r0[0])
		return r0

	def read_set_FP(ModbusClient):
		# reads setpoint power
		r0 = c.read_holding_registers(100, 1)
		# print('read_set_FP')
		# print(r0)
		return r0

	def read_freq(ModbusClient):
		# reads current frequency
		r0 = c.read_holding_registers(112, 1)
		# print('read_freq:')
		# print(r0)
		return r0



	while True:
		# sent hearbeat
		send_heartbeat(c)

		# read settings from database
		experiment_id, mw_fp_set, mw_freq_set = get_experiment_id(sql_engine, verbose=True)
		mw_fp_set = min(mw_fp_set, 200) # maximum 200
		mw_fp_set = int(mw_fp_set)

		mw_freq_set = 10 * mw_freq_set # convert to 10 times MHz
		mw_freq_set = min(mw_freq_set, 25000) # maximum 2.5 GHz
		mw_freq_set = int(mw_freq_set)
		print(' ')
		# sys.stdout.write(f"\n {mw_fp_set}, {mw_freq_set} ")
#
		# set start mode to tamp
		if RAMP_SET == False:
			RAMP_SET = set_start_mode_ramp(c)

		# set start time 60 s
		if RAMP_TIME_SET == False:
			RAMP_TIME_SET = set_start_time(c)

		# set the forward power set point to 200 W
		if FP_SET == False:
			FP_SET = set_FW_power(c, mw_fp_set)

		# set the reflected power set point to 100 W
		if RP_SET == False:
			RP_SET = set_RP(c)

		# set the reflected power set point to 100 W
		if FREQ_SET == False:
			FREQ_SET = set_freq(c, mw_freq_set)

		# set the microwave mode:
		if MODE_SET == False:
			 MODE_SET = set_microwave_mode(c)

		status = read_fault_present(c)
		forward_power = read_FP(c)
		reflected_power = read_RP(c)
		setpoint_power = read_set_FP(c)
		frequency_read = read_freq(c)


		# set the microwaves ON:
		if MW_ON == False:
			MW_ON = set_microwave_ON(ModbusClient)

		print(status, forward_power, reflected_power, setpoint_power, frequency_read)

		# save to DB
		# save_power_to_DB(forward_power[0], reflected_power[0], setpoint_power[0])
		# save_freq_to_DB(frequency_read[0], FREQUENCY_SETPOINT/10)

		status.insert(0, '104:')
		status.insert(2, ', 105:')
		status = [str(s) for s in status]
		print(status)
		saveDB(experiment_id, forward_power[0], mw_fp_set, reflected_power[0], frequency_read[0], mw_freq_set, 0, verbose=False)
		sleep(0.1)




if __name__ == '__main__':
	# Get the arguments from the command-line except the filename
	argv = sys.argv[1:]

	try:
		if len(argv) == 1:
			ip_address = argv[0][2:]
			live(ip_address)

		else:
			print('Error! usage: .py --ip_address. ip_address must be provided!')
			sys.exit(2)

	except getopt.GetoptError:
		# Print something useful
		print('Error! usage: .py --ip_address. ip_address must be provided!')
		sys.exit(2)

