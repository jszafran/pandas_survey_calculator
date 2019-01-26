# -*- coding: utf-8 -*-
"""
Quantitative Survey Calculator app
"""
import pandas as pd

class Survey:
    def __init__(self, name):
        self.name = name
        self.df = None
    
    def load_csv(self, path, nrows):
        self.df = pd.read_csv(filepath_or_buffer=path, nrows=nrows)


path = "<enter path here>\\resources"

