# -*- coding: utf-8 -*-
"""
Quantitative Survey Calculator app
"""
from surveyutils import surveyutils as su

import pandas as pd
import json
import copy
import time
import hashlib

class Survey:
    def __init__(self):
        self.df = None
        self.config = None
        self.questions = []
        self.cuts = []
        self.results = []
        self.utils = su.SurveyUtils
        self.result_file_hash = None

    def load_csv(self, path, nrows=None):
        """
        Loads initial dataset for survey from csv.
        """
        if nrows:
            self.df = pd.read_csv(filepath_or_buffer=path, nrows=nrows)
        else:
            self.df = pd.read_csv(filepath_or_buffer=path)

    def _parse_config(self, config_file):
        self.questions = self.utils.parse_config(config_file)

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
        if not isinstance(min, int) and not isinstance(max, int):
            raise TypeError
        return {k: 0 for k in range(min, max + 1)}

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
        self.cuts = self.utils.parse_cuts(cuts_file)

    def _calculate_counts(self, df, qsts_list, res_dict):
        res_dict['cut_respondents'] = df.shape[0]
        for qst in qsts_list:
            res_dict[qst]['qst_respondents'] = int(df[qst].value_counts().sum())
            for k,v in df[qst].value_counts().items():
                res_dict[qst][k] = v
        return res_dict

    def _get_current_time_hash(self):
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        return hash.hexdigest()

    def start_process(self, config_file, cuts_file, dump_threshold=100):
        self._parse_config('config.json')
        self._parse_cuts('cuts.json')
        print(f"dump threshold is {dump_threshold}")
        qsts_codes = self._get_questions_codes_list()
        empty_res_dict = self._prepare_empty_results()
        result_blueprint = {}
        for qst in self.questions:
            result_blueprint[qst.code] = copy.deepcopy(empty_res_dict[(qst.min_scale, qst.max_scale)])
        output_path = './output/'
        time_hashed = self._get_current_time_hash()
        self.result_file_hash = time_hashed
        res_count = 0
        # iterate through cut
        time1 = time.time()
        res_file_part_cnt = 1
        for idx, cut in enumerate(self.cuts):
            if cut.type_of_filter.upper() == 'ROLLUP':
                filtered_by_org_df = self.filter_by_org_unit(cut.org_unit)
            else:
                filtered_by_org_df = self.filter_by_org_unit(cut.org_unit,
                                                             "DIRECT")
            final_df = self.filter_by_demog_cut(filtered_by_org_df, cut.demogs)

            res = {}
            res[cut.id] = self._calculate_counts(final_df,
                                         qsts_codes,
                                         copy.deepcopy(result_blueprint))
            self.results.append(res)
            res_count+=1

            # if threshold is met or last cut is being calculated, dump to json
            if res_count >= dump_threshold or idx == len(self.cuts)-1:
                with open(output_path+time_hashed+'_'+str(res_file_part_cnt).zfill(4)+'.json', 'w') as outfile:
                    json.dump(self.results, outfile)
                self.results.clear()
                res_count = 0
                res_file_part_cnt += 1

        time2=time.time()
        print(f'It took {time2-time1}s to calculate all cuts. Hash of the results file: \n{self.result_file_hash}')

