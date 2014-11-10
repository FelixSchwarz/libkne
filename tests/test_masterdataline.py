# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

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
    
    def test_replace_unencodable_characters(self):
        # é is not part of the extended ASCII table defined by DATEV
        line = DataLine(key=103, text=u'Lenné')
        expected_binary = 't' + '103' + '\x1e' + 'Lenne' + '\x1c' + 'y'
        self.assertEqual(expected_binary, line.to_binary())

