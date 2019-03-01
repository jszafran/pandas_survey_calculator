"""
class for calculating final results
"""
from surveyutils import surveyutils as su
from config import resultsconfig as rc

class ResultsCalculator:
    def __init__(self, config_file, cuts_file, results_file_hash="#"):
        self.utils = su.SurveyUtils()
        self.questions = self.utils.parse_config(config_file)
        self.cuts = self.utils.parse_cuts(cuts_file)
        self.results_configs = rc.ResultsConfig.result_configs

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

