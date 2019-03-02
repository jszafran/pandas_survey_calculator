"""
class for calculating final results
"""
from surveyutils import surveyutils as su
from config import resultsconfig as rc

import json
import glob
import pprint
from collections import namedtuple
from time import time

class ResultsCalculator:
    def __init__(self, config_file, cuts_file, results_file_hash="#"):
        self.utils = su.SurveyUtils()
        self.questions = self.utils.parse_config(config_file)
        self.cuts = self.utils.parse_cuts(cuts_file)
        self.results_configs = rc.ResultsConfig.result_configs
        self.results = []
        self.results_file_hash = results_file_hash

    def _get_csv_header(self):
        header_list = []
        initial_fields = [
            "CUT_NAME",
            "RESPONDENTS",
        ]
        header_list += initial_fields
        for qst in self.questions:
            header_list += self._get_question_result_header(qst)

        return header_list

    def _get_question_result_header(self, qst):
        qst_header = [f'{qst.code}_respondents']
        qst_header += [f"{str(qst.code)}_{group_name}" for group_name in self.results_configs[qst.results_config]['groups_names']]
        qst_header += [f"{str(qst.code)}_{group_name}_count" for group_name in self.results_configs[qst.results_config]['groups_names']]
        return qst_header

    def _load_results(self):
        Result = namedtuple('Result', 'cut_id counts_dict')
        file_list = sorted(glob.glob(f'./output/{self.results_file_hash}*'))
        self.results.clear()
        for file in file_list:
            with open(file, 'r') as json_result:
                result = json.load(json_result)
                for dict in result:
                    for key in dict:
                        self.results.append(Result(key, dict[key]))

    def _get_question_sum_groups(self, qst_code):
        return rc.ResultsConfig.result_configs[list(filter(lambda qst: qst.code==qst_code, self.questions))[0].results_config]['groups']

    def _get_question_sum_groups_names(self, qst_code):
        return rc.ResultsConfig.result_configs[list(filter(lambda qst: qst.code==qst_code, self.questions))[0].results_config]['groups_names']

    def _calculate_cut_results(self, cut_result):
        qst_codes = [qst.code for qst in self.questions]
        cut_results = []
        cut_results += [cut_result.cut_id, cut_result.counts_dict['cut_respondents']]
        for qst in qst_codes:
            qst_groups = self._get_question_sum_groups(qst)
            counts_dict = cut_result.counts_dict[qst]
            qst_results = []
            qst_respondents = counts_dict['qst_respondents']
            # iterate over sum groups
            qst_results.append(qst_respondents)
            qst_percents = []
            qst_counts = []
            for idx, group in enumerate(qst_groups):
                if len(group) > 1:
                    res = 0
                    for el in group:
                        res += counts_dict[str(el)]
                else:
                    res = counts_dict[str(group[0])]
                qst_percents.append(res/qst_respondents)
                qst_counts.append(res)
            qst_results += (qst_percents + qst_counts)
            cut_results += qst_results
        return cut_results

    def start_process(self, output_file):
        print("<== starting calculating final results ==>")
        # writing header
        self._load_results()
        with open(output_file, 'a') as out:
            out.write('.'.join(self._get_csv_header()) + '\n')
            for cut_result in self.results:
                out.write('.'.join(str(v) for v in self._calculate_cut_results(cut_result)) + '\n')
        print("<== Results written to csv successfully.")
