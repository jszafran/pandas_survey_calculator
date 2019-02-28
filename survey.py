# -*- coding: utf-8 -*-
"""
Quantitative Survey Calculator app
"""
import resources
import json
import sys
import copy
import pprint
from collections import namedtuple
import time

import pandas as pd

class Survey:
    def __init__(self, name):
        self.name = name
        self.df = None
        self.config = None
        self.questions = []
        self.cuts = []
        self.results = []

    def load_csv(self, path, nrows=None):
        """
        Loads initial dataset for survey from csv.
        """
        if nrows:
            self.df = pd.read_csv(filepath_or_buffer=path, nrows=nrows)
        else:
            self.df = pd.read_csv(filepath_or_buffer=path)

    def _parse_config(self, config_file):
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
        Returns filtered dataframe based on cuts
        provided.
        """
        if df is None:
            return

        if not isinstance(d, dict):
            return

        df['_helper_col'] = 1==1
        hlp_srs = df['_helper_col']
        if not d:
            return df[hlp_srs]
        for k,v in d.items():
            hlp_srs = hlp_srs & (df[k]==v)
        return df[hlp_srs]

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
        """
        Parse and load data cuts for calculations.
        """
        with open(f'./resources/{cuts_file}', 'r') as json_file:
            cuts_data = json.load(json_file)
        Cut = namedtuple('Cut', 'id id_full org_unit type_of_filter demogs')
        for cut in cuts_data['cuts']:
            self.cuts.append(Cut(id=cut,
                                 id_full=cuts_data['cuts'][cut][0],
                                 org_unit=cuts_data['cuts'][cut][1],
                                 type_of_filter=cuts_data['cuts'][cut][2],
                                 demogs=cuts_data['cuts'][cut][3]
                                 ))

    def _calculate_counts(self, df, qsts_list, res_dict):
        res_dict['cut_respondents'] = df.shape[0]
        for qst in qsts_list:
            res_dict[qst]['qst_respondents'] = int(df[qst].value_counts().sum())
            for k,v in df[qst].value_counts().items():
                res_dict[qst][k] = v
        return res_dict

    def start_calculations(self, config_file, cuts_file, output_path):
        # parse config
        self._parse_config('config.json')
        # parse
        self._parse_cuts('cuts.json')

        qsts_codes = self._get_questions_codes_list()
        empty_res_dict = self._prepare_empty_results()
        result_blueprint = {}
        for qst in self.questions:
            result_blueprint[qst.code] = copy.deepcopy(empty_res_dict[(qst.min_scale, qst.max_scale)])

        # iterate through cut
        time1 = time.time()
        for cut in self.cuts:
            if cut.type_of_filter.upper() == 'ROLLUP':
                filtered_by_org_df = self.filter_by_org_unit(cut.org_unit)
            else:
                filtered_by_org_df = self.filter_by_org_unit(cut.org_unit,
                                                                 "DIRECT")
            final_df = self.filter_by_demog_cut(filtered_by_org_df, cut.demogs)

            res = self._calculate_counts(final_df,
                                   qsts_codes,
                                   copy.deepcopy(result_blueprint))
            self.results.append(res)
        time2=time.time()
        print(f'It took {time2-time1}s to calculate all cuts.')
        print('writing results to json')
        time1 = time.time()
        with open('results.json', 'w') as outfile:
            json.dump(self.results, outfile)
        time2 = time.time()
        print(f'Writing to json took {time2-time1}s.')
