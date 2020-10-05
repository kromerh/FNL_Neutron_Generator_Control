from pyModbusTCP.client import ModbusClient

# MAC Address of the microwave generator
# MAC Address: 00:80:A3:C2:AB:65 (Lantronix)

# sudo
try:
	# c = ModbusClient(host="169.254.150.42", port=502, auto_open=True, auto_close=True)
	c = ModbusClient(host="169.254.240.116", port=502, auto_open=True, auto_close=True)
	# c = ModbusClient(host="169.254.240.1", port=502, auto_open=True, auto_close=True)
except ValueError:
	print("Error with host or port params")

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
	wr = ModbusClient.write_single_coil(2,2)
	print('set_start_mode_ramp:' + str(int(wr)))
	return wr

def set_start_time(ModbusClient):
	# Sets the start time to 60s
	# c is ModbusClient
	wr = ModbusClient.write_single_register(4,200)
	print('set_start_time:' + str(int(wr)))
	return wr

def set_FW_power(ModbusClient):
	# Sets the forward power set point to 200 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(0,0)
	print('set_FW_power:' + str(int(wr)))
	return wr

def set_RP(ModbusClient):
	# Sets the reflected power set point to 100 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(1,1)
	print('set_RP:' + str(int(wr)))
	return wr

def set_freq(ModbusClient):
	# Sets the reflected power set point to 100 W
	# c is ModbusClient
	wr = ModbusClient.write_single_register(9,24000)
	print('set_freq:' + str(int(wr)))
	return wr

def set_microwave_mode(ModbusClient):
	# Sets the microwave mode:
	#	autotuning on, reflected power RP limitation, reset faults
	# c is ModbusClient
	bit_addr = 2
	bit_value = 0 # 0 0 0 0 0 0 0 0
	wr = c.write_single_register(bit_addr, bit_value)
	print('set_microwave_mode:' + str(int(wr)))
	return wr

def set_microwave_ON(ModbusClient):
	# Sets the microwave mode:
	#	autotuning on, reflected power RP limitation, MW ON, reset faults
	# c is ModbusClient
	bit_addr = 2
	bit_value = 210 # 0 1 0 0 1 0 1 1
	wr = c.write_single_register(bit_addr, bit_value)
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



while True:
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




# while True:
# 	wr = c.write_single_register(20, 128) # modbus heartbeat
# 	rr = c.read_holding_registers(99, 1)
# 	r0 = c.read_holding_registers(105, 1)
# 	print(r0)

# addr = 104
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)

# addr = 108
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)


# addr = 102
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)

