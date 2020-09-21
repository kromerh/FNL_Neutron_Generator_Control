import re
import sys
import sqlalchemy as sql
import datetime
import time
from time import sleep
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np

# Settings for the simulator
# path
PATH_CREDENTIALS = '/Users/hkromer/02_PhD/01.github/FNL_Neutron_Generator_Control/credentials.pw'

# readout frequency
FREQUENCY = 1 # sleep time in second


# values to save
MW_FP_SETPOINT = 0 # W
MW_FP = 200 # W
MW_RP = 0 # W
MW_FREQ = 2450.0 # MHz
MW_FREQ_SET = 2450.0 # MHz
CODE = 0 # Error code



VERBOSE = True


# read password and user to database

credentials = pd.read_csv(PATH_CREDENTIALS, header=0)

user = credentials['username'].values[0]
pw = credentials['password'].values[0]
host = str(credentials['hostname'].values[0])
db = str(credentials['db'].values[0])

connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}
sql_engine = sql.create_engine(connect_string)




def get_experiment_id_and_setpoint(sql_engine, verbose=False):
    query = f"SELECT * FROM experiment_control;"
    df = pd.read_sql(query, sql_engine)

    experiment_id = df['experiment_id'].values[0]
    mw_fp_set = df['mw_fp_set'].values[0]
    mw_freq_set = df['mw_freq_set'].values[0]

    if verbose: print(f"Experiment id is {experiment_id}")

    return experiment_id, mw_fp_set, mw_freq_set





def saveDB(experiment_id, fp, fp_set, rp, freq, freq_set, code, verbose=False):
    # Create a Cursor object to execute queries.
    query = f"""INSERT INTO live_mw (experiment_id, fp, fp_set, rp, freq, freq_set, code) VALUES (\"{experiment_id}\", \"{fp}\", \"{fp_set}\", \"{rp}\", \"{freq}\", \"{freq_set}\", \"{code}\");"""
    sql_engine.execute(sql.text(query))

    if verbose: print(query)


while True:
    try:

        experiment_id, mw_fp_set, mw_freq_set = get_experiment_id_and_setpoint(sql_engine, VERBOSE)
        rp = np.random.randint(0, 15) # draw a random number of PR
        fp = mw_fp_set - rp
        freq = mw_freq_set - np.random.randint(10, 100)
        fp_set = mw_fp_set
        freq_set = mw_freq_set
        code = CODE
        saveDB(experiment_id, fp, fp_set, rp, freq, freq_set, code, VERBOSE)

        sleep(FREQUENCY)
    except KeyboardInterrupt:
        print('Ctrl + C. Exiting. Flushing serial connection.')
        sys.exit(1)


