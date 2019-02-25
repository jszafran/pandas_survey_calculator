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
        self.cuts = []

    def load_csv(self, path, nrows=None):
        """
        Loads initial dataset for survey from csv.
        """
        if nrows:
            self.df = pd.read_csv(filepath_or_buffer=path, nrows=nrows)
        else:
            self.df = pd.read_csv(filepath_or_buffer=path)

    def parse_config(self, config_file):
        """
        Parsing basic information about questions (code, text, scale)
        from config file.
        """
        Question = namedtuple('Question', 'code text min_scale max_scale')
        with open(f'./config/{config_file}', 'r') as json_file:
            data = json.load(json_file)
        for qst_code in data['qsts']:
            self.questions.append(Question(code = qst_code,
                                           text=data['qsts'][qst_code][0],
                                           min_scale=int(data['qsts'][qst_code][1]),
                                           max_scale=int(data['qsts'][qst_code][2])))

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

    def _convert_min_max_range_to_dict(self, min, max):
        """
        Helper method for generating dictionary with min
        and max sequence with 0 counts initialized for them.
        """
        res = {}
        for i in range(min, max + 1):
            res[i] = 0
        return res

    def _prepare_empty_results(self):
        """
        Prepares dictionary with empty results based on
        questions scales from config file.
        """
        if not self.questions:
            return None
        empty_results = {}
        for question in self.questions:
            if not (question.min_scale, question.max_scale) in empty_results:
                empty_results[(question.min_scale, question.max_scale)] = (
                self._convert_min_max_range_to_dict(question.min_scale,
                                                    question.max_scale))
        return empty_results

    def _get_questions_codes_list(self):
        """
        Returns list of questions codes.
        """
        if not self.questions:
            return None

        return [question.code for question in self.questions]

    def _parse_cuts(self, cuts_file):
        with open(f'./resources/{cuts_file}', 'r') as json_file:
            cuts_data = json.load(json_file)
        Cut = namedtuple('Cut', 'id id_full org_node demogs')
        for cut in cuts_data['cuts']:
            self.cuts.append(Cut(id=cut,
                                 id_full=cuts_data['cuts'][cut][0],
                                 org_node=cuts_data['cuts'][cut][1],
                                 demogs=cuts_data['cuts'][cut][2]
                                 ))
