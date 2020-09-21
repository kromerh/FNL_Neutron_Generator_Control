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
ARD_TIME = 34386.0
COUNTS_BASE_1 = 5000/4
COUNTS_BASE_2 = 2000/4

VERBOSE = True

ALTERNATE_FREQ = 10 # how many seconds to switch from one value to the next

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


def saveDB(experiment_id, ard_time, counts_D1, counts_D2, counts_D3, counts_D4, verbose=False):
    # Create a Cursor object to execute queries.
    query = f"""INSERT INTO live_ref_det (experiment_id, ard_time, counts_D1, counts_D2, counts_D3, counts_D4) VALUES (\"{experiment_id}\", \"{ard_time}\", \"{counts_D1}\", \"{counts_D2}\", \"{counts_D3}\", \"{counts_D4}\");"""
    sql_engine.execute(sql.text(query))

    if verbose: print(query)


cnt = 0
COUNTS_BASE = COUNTS_BASE_1
alternate = True
while True:
    try:
        if cnt == ALTERNATE_FREQ:
            cnt = 0
            if alternate:
                COUNTS_BASE = COUNTS_BASE_2
                alternate = False
            else:
                COUNTS_BASE = COUNTS_BASE_1
                alternate = True

        experiment_id = get_experiment_id(sql_engine, VERBOSE)
        ard_time = ARD_TIME
        counts_D1 = (COUNTS_BASE+(np.random.random(1)-0.5)*1000)[0]
        counts_D2 = (COUNTS_BASE+(np.random.random(1)-0.5)*1000)[0]
        counts_D3 = (COUNTS_BASE+(np.random.random(1)-0.5)*1000)[0]
        counts_D4 = (COUNTS_BASE+(np.random.random(1)-0.5)*1000)[0]

        saveDB(experiment_id, ard_time, counts_D1, counts_D2, counts_D3, counts_D4, VERBOSE)

        sleep(FREQUENCY)
        cnt += 1
    except KeyboardInterrupt:
        print('Ctrl + C. Exiting. Flushing serial connection.')
        sys.exit(1)
    #finally:
     #   pi_flush(arduinoPort)

