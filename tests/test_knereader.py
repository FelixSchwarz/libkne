# -*- coding: UTF-8 -*-

from datetime import date
from decimal import Decimal
import os
import unittest


from libkne import KneFileReader


class TestKneReaderLxOffice(unittest.TestCase):
    def get_data_filenames(self, datadir):
        file_dir = os.path.dirname(__file__)
        abs_dir = os.path.abspath(os.path.join(file_dir, datadir))
        header = os.path.join(abs_dir, 'EV01')
        data_fp = os.path.join(abs_dir, 'ED00001')
        return (header, [data_fp])
    
    
    def setUp(self):
        datadir = os.path.join('testdata', 'lxoffice')
        header, data_fps = self.get_data_filenames(datadir)
        self.reader = KneFileReader(header, data_fps)
    
    
    def test_read_global_config(self):
        config = self.reader.get_config()
        self.assertEqual(471156, config["advisor_number"])
        self.assertEqual("Foo Bar", config["advisor_name"])
        #self.assertEqual(42212, config["client_number"])
        
        self.assertEqual(1, config["number_data_files"])
        self.assertEqual(1, config["number_last_data_file"])
        self.assertEqual(1, config["data_carrier_number"])
    
    
    def test_read_posting_lines(self):
        pass
        #self.assertEqual(1, config["accounting_number"])
        
        #self.assertEqual(date(2008, 05, 01), config["date_start"])
        #self.assertEqual(date(2008, 06, 15), config["date_end"])
        
        
    # Check the posting lines

