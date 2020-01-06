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
    def __init__(self, allowed_error=0.01, trial_count=10):
        self.allowed_error = allowed_error
        self.trial_count = trial_count

    def connect(self, user, password, db, host, port=8086):
        self.client = DataFrameClient(host, port, user, password, db)
        if not self.client.ping():
            print('Connection: FAILED\n')
            sys.exit(1)

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
        df_indiv = ci_reduction_parallel(df[param], max_rep_count=self.trial_count)
        return calculate_reps(df_indiv, self.allowed_error)

    def get_machine_details(self, predicate):
        where_clause = list()
        for key, value in predicate.items():
            where_clause.append(" \"{}\" = \'{}\' ".format(key, value))
        where_clause = " and ".join(where_clause)

        query = "select * from machine_information where {}".format(where_clause)
        logging.info('Query: {}'.format(query))

        df = self.client.query(query)['machine_information']
        return df.to_dict(orient = "records")

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