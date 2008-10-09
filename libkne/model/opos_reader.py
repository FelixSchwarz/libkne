# -*- coding: UTF-8 -*-

import csv

class OposReader(object):
    def __init__(self, *args, **kwargs):
        class SemikolonSeparator(csv.excel):
            delimiter = ';'
        
        self.reader = csv.DictReader(dialect=SemikolonSeparator, *args, **kwargs)
    
    def __iter__(self):
        return self.reader

