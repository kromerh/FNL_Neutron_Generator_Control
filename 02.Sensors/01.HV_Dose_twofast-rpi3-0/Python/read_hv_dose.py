import serial
import re
import sys
import pymysql
import time
from time import sleep
from scipy.interpolate import interp1d
import pandas as pd

db = pymysql.connect(host="twofast-RPi3-0",  # your host
                     user="logger",  # username
                     passwd="logger",  # password
                     db="FNL_DB")  # name of the database

arduinoPort = '/dev/ttyACM0'  # might need to be changed if another arduino is plugged in or other serial
serialArduino = serial.Serial(port=arduinoPort, baudrate=9600)

def saveDB(dose_voltage, HV_current, HV_voltage):
    # Create a Cursor object to execute queries.
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO live_hv_dose (HV_current, HV_voltage, dose_voltage) VALUES (%s, %s, %s)""", (HV_current, HV_voltage, dose_voltage))
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
    while (serialArduino.inWaiting() == 0):  # wait for incoming data
        pass
    valueRead = serialArduino.readline()
    try:
        valueRead = (valueRead.decode('utf-8')).strip()
    except UnicodeDecodeError:
        valueRead = '-1'
    return valueRead

# calibrate HV voltage

# correct the HV that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
df_HV_LT = pd.read_csv('./HV_readout    _calibration.txt', delimiter="\t")

# interpolation function
interp_HV_voltage = interp1d(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])

# correct the current that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
df_HV_I_LT = pd.read_csv('./I_readout_calibration.txt', delimiter="\t")

# interpolation function
interp_HV_current = interp1d(df_HV_I_LT['Current_read'], df_HV_I_LT['HV_current'])


counts_WS = 0
counts_BS = 0

while True:
    try:
        # t0 = time.time()
        ardRead = pi_read()
        # print(time.time() - t0)
        pi_flush(arduinoPort)
        s = ardRead.rstrip().split()
        print(s)
        if len(s) == 5:  # V1  V2  Abs(V2 - V1) V3  V4
            voltage_dose = float(s[2])
            HV_current = float(s[3])  # 0 - 2 mA
            HV_voltage = float(s[4])  # -(0-150) kV
            HV_voltage = float(interp_HV_voltage(HV_voltage))
            HV_current = float(interp_HV_current(HV_current))
            # print(HV_voltage)
            saveDB(voltage_dose, HV_current, HV_voltage)

        sleep(0.01)
    except KeyboardInterrupt:
        print('Ctrl + C. Exiting. Flushing serial connection.')
        pi_flush(arduinoPort)
        sys.exit(1)
    finally:
        pi_flush(arduinoPort)

