"""
configuration for interpreting survey results,
setting up the way counts are summed etc.
"""

class ResultsConfig:
    result_configs = {
            "standard": {
                "groups": [(1, 2,), (3,), (4,), (5,6,)],
                "groups_names": ["1+2", "3", "4", "5+6"]
            },
            "custom_example": {
                "groups": [(1,2,3,), (4,5,), (6,)],
                "groups_names": ["1+2+3", "4", "5+6"]
            },
            "weird": {
                "groups": [(1,2,), (3,)],
                "groups_names": ["1+2", "3"]
            },
            "tens": {
                "groups": [(1,2,3,), (4,5,6,), (7,8,), (9,), (10,)],
                "groups_names": ["gr_1_", "gr_2_", "gr_3_", "gr_4_", "gr_5_"]
            }
        }


