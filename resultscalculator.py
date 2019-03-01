"""
class for calculating final results
"""
from surveyutils import surveyutils as su
from config import resultsconfig as rc

import json
import glob
import pprint
from collections import namedtuple

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

        return ",".join(header_list)

    def _get_question_result_header(self, qst):
        qst_header = [f'{qst.code}_respondents']
        print(self.results_configs['standard']['groups_names'])
        qst_header += [f"{str(qst.code)}_{group_name}" for group_name in self.results_configs[qst.results_config]['groups_names']]
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

    def _calculate_cut_results(self, cut_name, counts_dict):
        sum_groups = self._get_question_sum_groups("Q1")
        print(sum_groups)
        pprint.pprint(counts_dict)



