import serial
import serial.tools.list_ports
import re
import sys
import pymysql
from time import sleep
import time
import pandas as pd
import numpy as np

db = pymysql.connect(host="twofast-RPi3-0",  # your host
                     user="logger",  # username
                     passwd="logger",  # password
                     db="FNL_DB")  # name of the database

arduinoPort = '/dev/ttyACM0'
serialArduino = serial.Serial(port=arduinoPort, baudrate=9600)

def saveDB(volt_1, volt_2):
    # Create a Cursor object to execute queries.
    # voltage 1 is ion source
    # voltage 2 is vacuum chamber
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO live_pressure (voltage_IS, voltage_VC) VALUES (%s, %s)""", (volt_1, volt_2))
    except:
        cur.rollback()

    db.commit()
    cur.close()

def fun_read_serial_ports():
    return list(serial.tools.list_ports.comports())

def pi_flush(serial_port):
    serialArduino = serial.Serial(port=serial_port, baudrate=9600)
    serialArduino.flushInput()  #flush input buffer, discarding all its contents
    serialArduino.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer

def pi_read():
    serialArduino = serial.Serial(port=arduinoPort, baudrate=9600)
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


counts_WS = 0
counts_BS = 0
# readout of the arduino
# pi_flush(arduinoPort)
while True:
    try:

        ardRead = pi_read()
        # pi_flush(arduinoPort)
        # print(ardRead)

        # print(time.time() - t0)
        s = ardRead.rstrip().split()
        # sys.stdout.write('...running BBox reader...')
        if len(s) == 5:  # V1 V2 extractionOn
            print(s)
            volt_1 = s[0]
            volt_2 = s[1]
            # start_time = time.time()

            saveDB(volt_1, volt_2)
            # print("%s seconds " % (time.time() - start_time))
        sleep(0.1)

    except KeyboardInterrupt:
        print('Ctrl + C. Exiting. Flushing serial connection.')
        pi_flush(arduinoPort)
        sys.exit(1)
    finally:
        pi_flush(arduinoPort)

