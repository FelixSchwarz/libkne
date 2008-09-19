# -*- coding: UTF-8 -*-

import datetime
from decimal import Decimal
import StringIO
import unittest


from libkne import DataLine

class TestMasterdataLine(unittest.TestCase):
    
    def test_simple_binary_writing(self):
        line = DataLine(key=103, text=u'Hans Schmidt')
        expected_binary = 't' + '103' + '\x1e' + 'Hans Schmidt' + '\x1c' + 'y'
        self.assertEqual(expected_binary, line.to_binary())
    
    def test_write_to_binary_with_nonascii_characters(self):
        line = DataLine(key=103, text=u'Müller')
        expected_binary = 't' + '103' + '\x1e' + 'M\x81ller' + '\x1c' + 'y'
        self.assertEqual(expected_binary, line.to_binary())

