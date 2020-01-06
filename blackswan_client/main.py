import os
import sys
import logging

import pandas as pd
import numpy as np
from influxdb import DataFrameClient

from blackswan_client.utils import *


logging.basicConfig(level=logging.INFO)

class BlackSwanAPI(object):
    """BlackSwan API Client library.
    """
    def __init__(self):
        self.allowed_err = 0
        self.trial_cnt = 0
        self.is_connected = False

    def connect(self, user, password, db, host, port=8086):
        self.client = DataFrameClient(host, port, user, password, db)
        if not self.client.ping():
            print('Connection: FAILED\n')
            sys.exit(1)
        else:
            self.is_connected = True

    def check_connection(fn):
        def wrapper(self, *args, **kwargs) :
            if not self.is_connected:
                logging.error("Client not connected to InfluxDB instance.")
                sys.exit(1)
            return fn(self, *args, **kwargs)
        return wrapper

    @check_connection
    def set_allowed_err_and_trial_cnt(self, allowed_err, trial_cnt):
        self.allowed_err = allowed_err
        self.trial_cnt = trial_cnt

    @check_connection
    def get_no_of_reps(self, machine_predicate, benchmark_predicate, param, test):
        mid_clause = list()
        mids = self.get_machine_ids(machine_predicate)
        for mid in mids:
            mid_clause.append(" \"mid\" = \'{}\' ".format(mid))
        mid_clause = " or ".join(mid_clause)
        mid_clause = "( " + mid_clause + ") "
        
        benchmark_clause = list()
        for key, value in benchmark_predicate.items():
            benchmark_clause.append(" \"{}\" = \'{}\' ".format(key, value))
        benchmark_clause = " and ".join(benchmark_clause)
        
        where_clause = benchmark_clause + " and " + mid_clause
        query = "select {} from {} where {}".format(param, test, where_clause)
        logging.info('Query: {}'.format(query))

        df = self.client.query(query)[test]
        df_indiv = ci_reduction_parallel(df[param], max_rep_count=self.trial_cnt)
        return calculate_reps(df_indiv, self.allowed_err)

    @check_connection
    def get_machine_details(self, predicate):
        where_clause = list()
        for key, value in predicate.items():
            where_clause.append(" \"{}\" = \'{}\' ".format(key, value))
        where_clause = " and ".join(where_clause)

        query = "select * from machine_information where {}".format(where_clause)
        logging.info('Query: {}'.format(query))

        df = self.client.query(query)['machine_information']
        return df.to_dict(orient = "records")

    @check_connection
    def get_machine_ids(self, predicate):
        where_clause = list()
        for key, value in predicate.items():
            where_clause.append(" \"{}\" = \'{}\' ".format(key, value))
        where_clause = " and ".join(where_clause)

        query = "select * from machine_information where {}".format(where_clause)
        logging.info('Query: {}'.format(query))

        df = self.client.query(query)['machine_information']
        result = df.to_dict(orient = "records")
        return [r['mid'] for r in result]