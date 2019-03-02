from config import resultsconfig
from collections import namedtuple
import json

class SurveyUtils:

    @classmethod
    def parse_config(cls, config_file):
        """
        Parsing basic information about questions (code, text, scale)
        from config file.
        """
        conf = resultsconfig.ResultsConfig()
        Question = namedtuple('Question', 'code text min_scale max_scale results_config')
        with open(f'./config/{config_file}', 'r') as json_file:
            data = json.load(json_file)
        return [Question(code = qst_code,
                         text=data['qsts'][qst_code][0],
                         min_scale=int(data['qsts'][qst_code][1]),
                         max_scale=int(data['qsts'][qst_code][2]),
                         results_config=data['qsts'][qst_code][3]) for qst_code in data['qsts']]

    @classmethod
    def parse_cuts(cls, cuts_file):
        """
        Parse and load data cuts for calculations.
        """
        with open(f'./resources/{cuts_file}', 'r') as json_file:
            cuts_data = json.load(json_file)
        Cut = namedtuple('Cut', 'id id_full org_unit type_of_filter demogs')
        return [Cut(id=cut,
                    id_full=cuts_data['cuts'][cut][0],
                    org_unit=cuts_data['cuts'][cut][1],
                    type_of_filter=cuts_data['cuts'][cut][2],
                    demogs=cuts_data['cuts'][cut][3]) for cut in cuts_data['cuts']]
