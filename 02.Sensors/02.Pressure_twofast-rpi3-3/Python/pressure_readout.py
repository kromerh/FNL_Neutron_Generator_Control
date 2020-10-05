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

    if verbose: print(f"Experiment id is {experiment_id}")

    return experiment_id


def saveDB(experiment_id, voltage_IS, voltage_VC, verbose=False):
    # Create a Cursor object to execute queries.
    query = f"""INSERT INTO live_pressure (experiment_id, voltage_IS, voltage_VC) VALUES (\"{experiment_id}\", \"{voltage_IS}\", \"{voltage_VC}\");"""
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

def simulate(FREQUENCY=1, VOLTAGE_IS_1=1, VOLTAGE_IS_2=3, VOLTAGE_VC=0, ALTERNATE_FREQ=30, VERBOSE=False):
    cnt = 0
    VOLTAGE_IS = VOLTAGE_IS_1

    alternate = True
    while True:
        try:
            if cnt == ALTERNATE_FREQ:
                cnt = 0
                if alternate:
                    VOLTAGE_IS = VOLTAGE_IS_2
                    alternate = False
                else:
                    VOLTAGE_IS = VOLTAGE_IS_1
                    alternate = True

            experiment_id = get_experiment_id(sql_engine, VERBOSE)

            voltage_IS = float(VOLTAGE_IS)
            voltage_VC = float(VOLTAGE_VC)

            saveDB(experiment_id, voltage_IS, voltage_VC, VERBOSE)

            sleep(FREQUENCY)
            cnt += 1
        except KeyboardInterrupt:
            print('Ctrl + C. Exiting. Flushing serial connection.')
            sys.exit(1)

def read_live():
    while True:
        try:
            # read arduino
            ardRead = pi_read(ARDUINO_PORT)
            s = ardRead.rstrip().split()
            sys.stdout.write('... reading out pressure ...')
            sys.stdout.write(f'{s}')
            if len(s) == 5:  # V1 V2 extractionOn
                print(s)
                volt_1 = s[0]
                volt_2 = s[1]

                voltage_IS = float(volt_1)
                voltage_VC = float(volt_2)
                print(voltage_IS, voltage_VC)
                # saveDB(experiment_id, voltage_IS, voltage_VC, VERBOSE)
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
            if MODE == '--simulate':
                simulate()
            elif MODE == '--live':
                read_live()
            else:
                print('Error! usage: pressure_readout.py --MODE. MODE can be simulate or live')
                sys.exit(2)
        else:
            print('Error! usage: pressure_readout.py --MODE. MODE can be simulate or live')
            sys.exit(2)

    except getopt.GetoptError:
        # Print something useful
        print('Error! usage: pressure_readout.py --MODE. MODE can be simulate or live')
        sys.exit(2)


