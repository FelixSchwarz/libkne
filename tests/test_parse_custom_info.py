# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

import unittest

from libkne import CustomInfoRecord


class TestCustomInfoRecord(unittest.TestCase):
    
    def test_parse_custom_info(self):
        binary_line = '\xb7Foo\x1c\xb8Bar\x1cy'
        custom_info, end_index = CustomInfoRecord.from_binary(binary_line, 0)
        self.assertEqual('Foo', custom_info.key)
        self.assertEqual('Bar', custom_info.value)
        self.assertEqual(len(binary_line) - 1, end_index)
    
    
    def test_write_custom_info_to_binary(self):
        binary_line = '\xb7Key\x1c\xb8Value\x1cy'
        custom_info = CustomInfoRecord('Key', 'Value')
        self.assertEqual(binary_line, custom_info.to_binary())

