# -*- coding: UTF-8 -*-

from datetime import date
from decimal import Decimal
import os
import unittest

from test_knereader_lxoffice import SampleDataReaderCase


class TestKneReaderMonkeyKassenbuch(SampleDataReaderCase):
    def setUp(self):
        super(TestKneReaderMonkeyKassenbuch, self).setUp('monkey_kassenbuch')
    
    def test_product_abbreviation(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        config = self.reader.get_config()
        self.assertEqual("MKEY", config['product_abbreviation'])


# TZ EasyBuch has many format errors, they are not reliable and there much too
# many errors to fix them myself.
#class TestKneReaderTZEasyBuch(SampleDataReaderCase):
#    def setUp(self):
#        super(TestKneReaderTZEasyBuch, self).setUp('tz_easybuch')
#    
#    def test_product_abbreviation(self):
#        self.assertEqual(1, self.reader.get_number_of_files())
#        config = self.reader.get_config()
#        self.assertEqual("-TZB", config['product_abbreviation'])



