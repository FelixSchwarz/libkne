# -*- coding: UTF-8 -*-

from datetime import date
from decimal import Decimal
import os
import unittest

from test_knereader_lxoffice import SampleDataReaderCase


class TestKneReaderMonkeyKassenbuch(SampleDataReaderCase):
    def setUp(self):
        datadir = 'monkey_kassenbuch_transactions'
        super(TestKneReaderMonkeyKassenbuch, self).setUp(datadir)
    
    def test_product_abbreviation(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        config = self.reader.get_config()
        self.assertEqual('MKEY', config['product_abbreviation'])



class TestKneReaderMonkeyKassenbuchAccountLabels(SampleDataReaderCase):
    def setUp(self):
        datafile = 'monkey_kassenbuch_account_labels'
        super(TestKneReaderMonkeyKassenbuchAccountLabels, self).setUp(datafile)
    
    def test_account_labels(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        dfile = self.reader.get_file(0)
        data_lines = dfile.get_master_data_lines()
        self.assertEqual(286, len(data_lines))
        line2 = data_lines[1]
        self.assertEqual(65, line2.key)
        self.assertEqual(u"Unbebaute Grundstücke", line2.text)



# TZ EasyBuch has many format errors, they are not reliable and there much too
# many errors to fix them myself.
#class TestKneReaderTZEasyBuch(SampleDataReaderCase):
#    def setUp(self):
#        super(TestKneReaderTZEasyBuch, self).setUp('tz_easybuch')
#    
#    def test_product_abbreviation(self):
#        self.assertEqual(1, self.reader.get_number_of_files())
#        config = self.reader.get_config()
#        self.assertEqual('-TZB', config['product_abbreviation'])



class TestKneReaderMMSKassenbuch(SampleDataReaderCase):
    def setUp(self):
        super(TestKneReaderMMSKassenbuch, self).setUp('mms_kassenbuch_transactions')
    
    def test_application_info(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        tfile = self.reader.get_file(0)
        self.assertEqual('SELF ID: 15540', tfile.get_metadata()['application_info'])
        config = self.reader.get_config()
        self.assertEqual('SELF', config['product_abbreviation'])



class TestKneReaderMMSKassenbuchAccountLabels(SampleDataReaderCase):
    def setUp(self):
        datafile = 'mms_kassenbuch_account_labels'
        super(TestKneReaderMMSKassenbuchAccountLabels, self).setUp(datafile)
    
    def test_account_labels(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        dfile = self.reader.get_file(0)
        data_lines = dfile.get_master_data_lines()
        self.assertEqual(19, len(data_lines))
        line15 = data_lines[14]
        self.assertEqual(4190, line15.key)
        self.assertEqual(u"Aushilfslöhne", line15.text)



