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


def saveDB(experiment_id, ard_time, counts_D1, counts_D2, counts_D3, counts_D4, verbose=False):
    # Create a Cursor object to execute queries.
    query = f"""INSERT INTO live_ref_det (experiment_id, ard_time, counts_D1, counts_D2, counts_D3, counts_D4) VALUES (\"{experiment_id}\", \"{ard_time}\", \"{counts_D1}\", \"{counts_D2}\", \"{counts_D3}\", \"{counts_D4}\");"""
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
    valueRead = serialArduino.readline(500)
    # print(valueRead)
    try:
        valueRead = (valueRead.decode('utf-8')).strip()
        serialArduino.flushInput()  #flush input buffer, discarding all its contents
        serialArduino.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer
       # print(valueRead)
    except UnicodeDecodeError:
        valueRead = '-1'
    return valueRead


def read_live():
    while True:
        try:
            # experiment_id = get_experiment_id(sql_engine, VERBOSE)

            # read arduino
            ardRead = pi_read(ARDUINO_PORT)
            s = ardRead.rstrip().split()
            now = datetime.datetime.now()
            now = now.strftime(format='%Y-%m-%d %H:%M:%S')
            print(f"{now}")
            print(s)
            if len(s) == 7:
                ard_time = s[1]
                counts_D1 = s[3]
                counts_D2 = s[4]
                counts_D3 = s[5]
                counts_D4 = s[6]
                # if float(ard_time) >= 30000.0:
                #     sys.stdout.write('Reading reference detectors  ...')
                #     sys.stdout.write(f'{now}, D1: {counts_D1}, D2: {counts_D2}, D3: {counts_D3}, D4: {counts_D4} ')
                #     # saveDB(experiment_id, ard_time, counts_D1, counts_D2, counts_D3, counts_D4, VERBOSE)
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
                print('Error! usage: refDet_readout.py --MODE. MODE can only be live')
                sys.exit(2)
        else:
            print('Error! usage: refDet_readout.py --MODE. MODE can only be live')
            sys.exit(2)

    except getopt.GetoptError:
        # Print something useful
        print('Error! usage: refDet_readout.py --MODE. MODE can only be live')
        sys.exit(2)