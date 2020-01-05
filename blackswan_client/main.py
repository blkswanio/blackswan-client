import os
import sys

import pandas as pd
import numpy as np
from influxdb import DataFrameClient

from blackswan_client.utils import ci_reduction_parallel, get_reps


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

    def get_no_of_reps_for_cpu_st(self, test_name, dvfs, socket, param):
        query = """
        select * from npb_cpu_st where \"socket\" = \'{}\' and \"testname\" = \'{}\'
        """
        df = self.client.query(query.format(socket, test_name))['npb_cpu_st']
        df_indiv = ci_reduction_parallel(df[param], max_rep_count=self.trial_count)
        return get_reps(df_indiv, self.allowed_error)

    def get_no_of_reps_for_cpu_mt(self, test_name, dvfs, socket, param):
        query = """
        select * from npb_cpu_mt where \"socket\" = \'{}\' and \"testname\" = \'{}\'
        """
        df = self.client.query(query.format(socket, test_name))['npb_cpu_mt']
        df_indiv = ci_reduction_parallel(df[param], max_rep_count=self.trial_count)
        return get_reps(df_indiv, self.allowed_error)
        
    def get_no_reps_for_membench(self, dvfs, socket, param):
        query = """
        select * from membench where \"socket\" = \'{}\'
        """
        df = self.client.query(query.format(socket))['membench']
        df_indiv = ci_reduction_parallel(df[param], max_rep_count=self.trial_count)
        return get_reps(df_indiv, self.allowed_error)

    def get_no_reps_for_stream(self, dvfs, socket, param):
        query = """
        select * from stream where \"socket\" = \'{}\'
        """
        df = self.client.query(query.format(socket))['stream']
        df_indiv = ci_reduction_parallel(df[param], max_rep_count=self.trial_count)
        return get_reps(df_indiv, self.allowed_error)

    def no_of_reps_for_fio(self, io_depth, type, device, param):
        query = """
        select * from fio where \"io_depth\" = \'{}\' and \"type\" = \'{}\' and \"device\" = \'{}\'
        """
        df = self.client.query(query.format(io_depth, type, device))['fio']
        df_indiv = ci_reduction_parallel(df[param], max_rep_count=self.trial_count)
        return get_reps(df_indiv, self.allowed_error)

    def get_machines(self, predicate):
        where_clause = list()
        for key, value in predicate.items():
            where_clause.append(" \"{}\" = \'{}\' ".format(key, value))
        where_clause = " and ".join(where_clause)
        query = "select * from machine_information where {}"
        df = self.client.query(query.format(where_clause))['machine_information']
        return df.to_dict(orient = "records")

    def get_machine_ids(self, predicate):
        where_clause = list()
        for key, value in predicate.items():
            where_clause.append(" \"{}\" = \'{}\' ".format(key, value))
        where_clause = " and ".join(where_clause)
        query = "select * from machine_information where {}"
        df = self.client.query(query.format(where_clause))['machine_information']
        result = df.to_dict(orient = "records")
        return [r['mid'] for r in result]