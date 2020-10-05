from pyModbusTCP.client import ModbusClient
from time import sleep
import sys
import getopt

# MAC Address of the microwave generator
# MAC Address: 00:80:A3:C2:AB:65 (Lantronix)

# find the ip address of the microwave
# sudo tcpdump -i eth1


# for ii in range(0,65535):
# 	returnlist = []
# 	for jj in range(0,2000):
# 		regs_list_1 = c.read_holding_registers(ii, jj)
# 		returnlist.append(regs_list_1)
# 	if not None in returnlist:
# 		print(ii, returnlist)

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
	print('set_start_mode_ramp:' + str(int(wr)))
	return wr

def set_start_time(ModbusClient):
	# Sets the start time to 60s
	# c is ModbusClient
	wr = ModbusClient.write_single_register(4,60)
	print('set_start_time:' + str(int(wr)))
	return wr

def set_FW_power(ModbusClient):
	# Sets the forward power set point to 200 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(0,1)
	# wr = ModbusClient.write_single_register(0,200)
	print('set_FW_power:' + str(int(wr)))
	return wr

def set_RP(ModbusClient):
	# Sets the reflected power set point to 100 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(1,100)
	print('set_RP:' + str(int(wr)))
	return wr

def set_freq(ModbusClient):
	# Sets the reflected power set point to 100 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(9,24400)
	print('set_freq:' + str(int(wr)))
	return wr

def set_microwave_mode(ModbusClient):
	# Sets the microwave mode:
	#	autotuning on, reflected power RP limitation, reset faults
	# c is ModbusClient
	bit_addr = 2
	bit_value = 146 # 0 1 0 0 1 0 0 1
	wr = ModbusClient.write_single_register(bit_addr, bit_value)
	print('set_microwave_mode:' + str(int(wr)))
	return wr

def set_microwave_ON(ModbusClient):
	# Sets the microwave mode:
	#	autotuning on, reflected power RP limitation, MW ON, reset faults
	# c is ModbusClient
	bit_addr = 2
	bit_value = 210 # 0 1 0 0 1 0 1 1
	wr = ModbusClient.write_single_register(bit_addr, bit_value)
	print('set_microwave_ON:' + str(int(wr)))
	return wr



def read_fault_present(ModbusClient):
	# reads if fault present
	r0 = c.read_holding_registers(105, 1)
	if (len(r0) > 0) and (r0[0] == 128):
		# something returned and message is Moduel Ready for Microwaves
		print('Ready for microwaves ')
		print(r0)
	else:
		print('Fault present:')
		print(r0)
		# read the type of fault
		r1 = c.read_holding_registers(104, 1)
		print('Type of fault:')
		print(r1)

def read_FP(ModbusClient):
	# reads forward power
	r0 = c.read_holding_registers(102, 10)
	print('read_FP :')
	print(r0)

def read_RP(ModbusClient):
	# reads reflected power
	r0 = c.read_holding_registers(103, 10)
	print('read_RP:')
	print(r0)

def read_set_FP(ModbusClient):
	# reads setpoint power
	r0 = c.read_holding_registers(100, 10)
	print('read_set_FP')
	print(r0)

def read_freq(ModbusClient):
	# reads current frequency
	r0 = c.read_holding_registers(112, 10)
	print('read_freq:')
	print(r0)

def live(ip_address):
	while True:
		c = ModbusClient(host=f"{ip_address}", port=502, auto_open=True, auto_close=True)

		# sent hearbeat
		send_heartbeat(c)

		# set start mode to tamp
		if RAMP_SET == False:
			RAMP_SET = set_start_mode_ramp(c)

		# set start time 60 s
		if RAMP_TIME_SET == False:
			RAMP_TIME_SET = set_start_time(c)

		# set the forward power set point to 200 W
		if FP_SET == False:
			FP_SET = set_FW_power(c)

		# set the reflected power set point to 100 W
		if RP_SET == False:
			RP_SET = set_RP(c)

		# set the reflected power set point to 100 W
		if FREQ_SET == False:
			FREQ_SET = set_freq(c)

		# set the microwave mode:
		if MODE_SET == False:
			 MODE_SET = set_microwave_mode(c)

		read_fault_present(c)
		read_FP(c)
		read_RP(c)
		read_set_FP(c)
		read_freq(c)

		# set the microwaves ON:
		if MW_ON == False:
			MW_ON = set_microwave_ON(c)

		sleep(0.01)

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

