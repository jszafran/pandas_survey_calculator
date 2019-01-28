# -*- coding: utf-8 -*-
"""
Quantitative Survey Calculator app
"""

import pandas as pd

class Survey:
    def __init__(self, name):
        self.name = name
        self.df = None
    
    def load_csv(self, path, nrows=None):
        if nrows:
            self.df = pd.read_csv(filepath_or_buffer=path, nrows=nrows)
        else:
            self.df = pd.read_csv(filepath_or_buffer=path)
        
    def fitler_data_by_org_unit(self, org_unit, filter_type="rollup"):
        """
        Method filtering dataset by org node provided.
        'Direct' filter type returns only respondents
        within particular unit, 'rollup' mode returns
        direct unit + all children results.
        """
        if self.df is None:
            return
        org_col_name = 'org_d'
        if filter_type == "direct":
            return self.df[self.df[org_col_name]==org_unit]
        return self.df[self.df[org_col_name].str.contains(org_unit)]

# path = "<enter path here>\\resources"
path = "/home/kuba/Desktop/my_projects/pandas_survey_calculator/resources/dummy_data_set.csv"

