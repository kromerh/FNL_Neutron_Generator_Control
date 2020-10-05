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


def get_experiment_id(sql_engine, verbose=False):
    query = f"SELECT experiment_id FROM experiment_control;"
    df = pd.read_sql(query, sql_engine)

    experiment_id = df['experiment_id'].values[0]

    if verbose: sys.stdout.write(f"Experiment id is {experiment_id}")

    return experiment_id


def saveDB(experiment_id, HV_voltage, HV_current, dose_voltage, verbose=False):
    # Create a Cursor object to execute queries.
    query = f"""INSERT INTO live_hv_dose (experiment_id, HV_voltage, HV_current, dose_voltage) VALUES (\"{experiment_id}\", \"{HV_voltage}\", \"{HV_current}\", \"{dose_voltage}\");"""
    sql_engine.execute(sql.text(query))

    if verbose: sys.stdout.write(query)

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

# this might be obsolete, not sure
# # calibrate HV voltage

# # correct the HV that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
# df_HV_LT = pd.read_csv('/home/pi/Documents/HV_readout_calibration.txt', delimiter="\t")
# # print(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])
# # interpolation function
# interp_HV_voltage = interp1d(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])

# # correct the current that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
# df_HV_I_LT = pd.read_csv('/home/pi/Documents/I_readout_calibration.txt', delimiter="\t")
# # print(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])
# # interpolation function
# interp_HV_current = interp1d(df_HV_I_LT['Current_read'], df_HV_I_LT['HV_current'])

def read_live():
    while True:
        try:
            experiment_id = get_experiment_id(sql_engine, VERBOSE)

            # read arduino
            ardRead = pi_read(ARDUINO_PORT)
            s = ardRead.rstrip().split()
            now = datetime.datetime.now()
            now = now.strftime(format='%Y-%m-%d %H:%M:%S')
            print(' ')
            if len(s) == 5:
                dose_voltage = float(s[2])
                HV_current = float(s[3])  # 0 - 2 mA
                HV_voltage = float(s[4])  # -(0-150) kV
                # HV_voltage = float(interp_HV_voltage(HV_voltage))
                # HV_current = float(interp_HV_current(HV_current))
                # print(HV_voltage)

                voltage_IS = float(s[0])
                voltage_VC = float(s[1])
                sys.stdout.write('Reading hv and dose voltages  ...')
                sys.stdout.write(f'{now}, HV: {HV_voltage}, I: {HV_current}, dose: {dose_voltage} ')
                saveDB(experiment_id, HV_voltage, HV_current, dose_voltage, VERBOSE)
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
                print('Error! usage: hv_and_dose_readout.py --MODE. MODE can only be live')
                sys.exit(2)
        else:
            print('Error! usage: hv_and_dose_readout.py --MODE. MODE can only be live')
            sys.exit(2)

    except getopt.GetoptError:
        # Print something useful
        print('Error! usage: hv_and_dose_readout.py --MODE. MODE can only be live')
        sys.exit(2)