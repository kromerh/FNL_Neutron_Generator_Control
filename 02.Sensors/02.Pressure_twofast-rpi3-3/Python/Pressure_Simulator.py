import re
import sys
import sqlalchemy as sql
import datetime
import time
from time import sleep
from scipy.interpolate import interp1d
import pandas as pd

class Pressure_Simulator(object):
    """docstring for Pressure_Simulator"""
    def __init__(self, arg):
        super(Pressure_Simulator, self).__init__()

        # Settings for the simulator
        # path
        self.PATH_CREDENTIALS = '~/credentials.pw'

        # readout frequency
        self.FREQUENCY = 1 # sleep time in second


        # values to save
        self.VOLTAGE_IS_1 = 1 # V
        self.VOLTAGE_IS_2 = 3 # V
        self.VOLTAGE_VC = 0 # V

        self.VERBOSE = True

        self.ALTERNATE_FREQ = 10 # how many seconds to switch from one value to the next

        # read password and user to database

        credentials = pd.read_csv(self.PATH_CREDENTIALS, header=0)

        user = str(credentials['username'].values[0])
        pw = str(credentials['password'].values[0])
        host = str(credentials['hostname'].values[0])
        db = str(credentials['db'].values[0])

        connect_string = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:3306/%(db)s'% {"user": user, "pw": pw, "host": host, "db": db}

        self.sql_engine = sql.create_engine(connect_string)




    def get_experiment_id(self, verbose=False):
        query = f"SELECT experiment_id FROM experiment_control;"
        df = pd.read_sql(query, self.sql_engine)

        experiment_id = df['experiment_id'].values[0]

        if verbose: print(f"Experiment id is {experiment_id}")

        return experiment_id


    def saveDB(self, experiment_id, voltage_IS, voltage_VC, verbose=False):
        # Create a Cursor object to execute queries.
        query = f"""INSERT INTO live_pressure (experiment_id, voltage_IS, voltage_VC) VALUES (\"{experiment_id}\", \"{voltage_IS}\", \"{voltage_VC}\");"""
        self.sql_engine.execute(sql.text(query))

        if verbose: print(query)

    def simulate(self, FREQUENCY=1, VOLTAGE_IS_1=1, VOLTAGE_IS_2=3, VOLTAGE_VC=0, ALTERNATE_FREQ=30, VERBOSE=False):
        cnt = 0
        VOLTAGE_IS = self.VOLTAGE_IS_1

        alternate = True
        while True:
            try:
                if cnt == self.ALTERNATE_FREQ:
                    cnt = 0
                    if alternate:
                        VOLTAGE_IS = self.VOLTAGE_IS_2
                        alternate = False
                    else:
                        VOLTAGE_IS = self.VOLTAGE_IS_1
                        alternate = True

                experiment_id = self.get_experiment_id(self.VERBOSE)

                voltage_IS = float(VOLTAGE_IS)
                voltage_VC = float(VOLTAGE_VC)

                self.saveDB(experiment_id, voltage_IS, voltage_VC, self.VERBOSE)

                sleep(self.FREQUENCY)
                cnt += 1
            except KeyboardInterrupt:
                print('Ctrl + C. Exiting. Flushing serial connection.')
                sys.exit(1)


