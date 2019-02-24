# -*- coding: utf-8 -*-
"""
Quantitative Survey Calculator app
"""
import resources
import json
from collections import namedtuple

import pandas as pd

class Survey:
    def __init__(self, name):
        self.name = name
        self.df = None
        self.config = None
        self.questions = []

    def load_csv(self, path, nrows=None):
        if nrows:
            self.df = pd.read_csv(filepath_or_buffer=path, nrows=nrows)
        else:
            self.df = pd.read_csv(filepath_or_buffer=path)

    def parse_config(self, config_file):
        # initialize questions named tuples
        Question = namedtuple('Question', 'text min_scale max_scale')
        with open(f'./config/{config_file}', 'r') as json_file:
            data = json.load(json_file)
        for qst in data['qsts']:
            self.questions.append(Question(text=data['qsts'][qst][0],
                                           min_scale=data['qsts'][qst][1],
                                           max_scale=data['qsts'][qst][2]))

    def filter_by_org_unit(self, org_unit, filter_type="ROLLUP"):
        """
        Method filtering dataset by org node provided.
        'Direct' filter type returns only respondents
        within particular unit, 'rollup' mode returns
        direct unit + all children results.
        """
        if self.df is None:
            return

        if filter_type.upper() not in ["ROLLUP", "DIRECT"]:
            return

        org_col_name = "org_d"
        if filter_type.upper() == "DIRECT":
            return self.df[self.df[org_col_name]==org_unit]
        return self.df[self.df[org_col_name].str.contains(org_unit)]

    def filter_by_demog_cut(self, df, d):
        """
        Method accepts a dataframe and dictionary
        containing demog_name: demog_value pairs.
        Returns series of bools which is result
        of filtering conditions intersection.
        """
        if df is None:
            return

        if not isinstance(d, dict):
            return

        df['_helper_col'] = 1==1
        hlp_srs = df['_helper_col']
        if not d:
            return hlp_srs
        for k,v in d.items():
            hlp_srs = hlp_srs & (df[k]==v)
        return hlp_srs
