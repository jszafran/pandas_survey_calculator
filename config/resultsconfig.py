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
            }
        }


