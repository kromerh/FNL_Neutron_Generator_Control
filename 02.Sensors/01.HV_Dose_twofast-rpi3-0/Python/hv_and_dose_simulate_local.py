import re
import sys
import sqlalchemy as sql
import datetime
import time
from time import sleep
from scipy.interpolate import interp1d
import pandas as pd


# Settings for the simulator
# path
PATH_CREDENTIALS = '/Users/hkromer/02_PhD/01.github/FNL_Neutron_Generator_Control/credentials.pw'
HV_CALIB_FILE = '/Users/hkromer/02_PhD/01.github/phd/01_neutron_generator_contol/FNL/hv_and_dose/HV_readout_calibration.txt'
I_CALIB_FILE = '/Users/hkromer/02_PhD/01.github/phd/01_neutron_generator_contol/FNL/hv_and_dose/I_readout_calibration.txt'

# readout frequency
FREQUENCY = 1 # sleep time in second


# values to save
HV_VOLTAGE_1 = 1.2 # V
HV_VOLTAGE_2 = 3.2 # V

HV_CURRENT_1 = 0.1 # V
HV_CURRENT_2 = 0.9 # V

DOSE_VOLTAGE_1 = 1 # V
DOSE_VOLTAGE_2 = 1.9 # V


ALTERNATE_FREQ = 30 # how many seconds to switch from one value to the next

VERBOSE = True


# read password and user to database

credentials = pd.read_csv(PATH_CREDENTIALS, header=0)

user = credentials['username'].values[0]
pw = credentials['password'].values[0]
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)







def get_experiment_id(sql_engine, verbose=False):
    query = f"SELECT experiment_id FROM experiment_control;"
    df = pd.read_sql(query, sql_engine)

    experiment_id = df['experiment_id'].values[0]

    if verbose: print(f"Experiment id is {experiment_id}")

    return experiment_id



def saveDB(experiment_id, dose_voltage, HV_current, HV_voltage, verbose=False):
    # Create a Cursor object to execute queries.
    query = f"""INSERT INTO live_hv_dose (experiment_id, HV_voltage, HV_current, dose_voltage) VALUES (\"{experiment_id}\", \"{HV_voltage}\", \"{HV_current}\", \"{dose_voltage}\");"""
    sql_engine.execute(sql.text(query))

    if verbose: print(query)

# calibrate HV voltage

# correct the HV that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
df_HV_LT = pd.read_csv(HV_CALIB_FILE, delimiter="\t")
# print(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])
# interpolation function
interp_HV_voltage = interp1d(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'], fill_value="extrapolate")

# correct the current that the arduino reads. This is done using the dose_lookup_table which relates the pi dose with the displayed dose.
df_HV_I_LT = pd.read_csv(I_CALIB_FILE, delimiter="\t")
# print(df_HV_LT['Voltage_read'], df_HV_LT['HV_voltage'])
# interpolation function
interp_HV_current = interp1d(df_HV_I_LT['Current_read'], df_HV_I_LT['HV_current'])


# readout of the arduino
# pi_flush(arduinoPort)
cnt = 0
HV_VOLTAGE = HV_VOLTAGE_2
HV_CURRENT = HV_CURRENT_2
DOSE_VOLTAGE = DOSE_VOLTAGE_2
alternate = True
while True:
    try:
        if cnt == ALTERNATE_FREQ:
            cnt = 0
            if alternate:
                HV_VOLTAGE = HV_VOLTAGE_1
                HV_CURRENT = HV_CURRENT_1
                DOSE_VOLTAGE = DOSE_VOLTAGE_1
                alternate = False
            else:
                HV_VOLTAGE = HV_VOLTAGE_2
                HV_CURRENT = HV_CURRENT_2
                DOSE_VOLTAGE = DOSE_VOLTAGE_2
                alternate = True

        experiment_id = get_experiment_id(sql_engine, VERBOSE)
        dose_voltage = float(DOSE_VOLTAGE)
        HV_current = float(HV_CURRENT)  # 0 - 2 mA
        HV_voltage = float(HV_VOLTAGE)  # -(0-150) kV
        HV_voltage = float(interp_HV_voltage(HV_VOLTAGE))
        HV_current = float(interp_HV_current(HV_CURRENT))
        saveDB(experiment_id, dose_voltage, HV_current, HV_voltage, VERBOSE)

        sleep(FREQUENCY)
        cnt += 1
    except KeyboardInterrupt:
        print('Ctrl + C. Exiting. Flushing serial connection.')
        sys.exit(1)



