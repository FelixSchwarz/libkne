# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

import logging
import unittest

from libkne.model import KNEAddress

logging.basicConfig(level=logging.ERROR)


class TestKNEAddress(unittest.TestCase):
    def _assert_line_contents(self, key_text_tuples, computed_data):
        self.assertEqual(len(key_text_tuples), len(computed_data))
        for x in zip(key_text_tuples, computed_data):
            print 'x', repr(x)
        for (key, text), data in zip(key_text_tuples, computed_data):
            self.assertEqual(key, data.key)
            self.assertEqual(text, data.text)
    
    
    def test_cut_long_strings(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.degree = 'Dipl.-Inform. (Univ) / Foo Bar Master Manager (BA)'
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(3, len(lines))
    
    
    def test_transform_int_into_unicode_string(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.appellation = 5
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(3, len(lines))
    
    
    def test_distribute_long_values_acrosss_multiple_lines(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.name = 'Foo Bar Baz Qux Quux Quuux Quuuux Quuuuux Barfoo'
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(4, len(lines))
        expected = [(103, 'Foo Bar Baz Qux Quux Quuux Quuuux Quuuuu'), 
                    (203, 'x Barfoo')]
        self._assert_line_contents(expected, lines[2:])
    
    
    def test_cut_splitted_values_if_too_long(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.name = 'y'*40 + 'x'*30 + 'z'*30
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(4, len(lines))
        self._assert_line_contents([(103, 'y'*40), (203, 'x'*30 + 'z'*10)], 
                                   lines[2:])
    
    
    def test_strip_whitespace_distributed_values(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.name = ' Foo Bar '
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(3, len(lines))
        self._assert_line_contents([(103, 'Foo Bar')], lines[2:])
    
    
    def test_strip_whitespace_in_normal_values(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.degree = ' Ph.D. '
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(3, len(lines))
        self._assert_line_contents([(801, 'Ph.D.')], lines[2:])
    
    
    def test_no_not_strip_whitespace_within_distributed_values(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.name = ' F' + 'o' * 38 + ' ' + 'Bar '
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(4, len(lines))
        self._assert_line_contents([(103, 'F' + 'o'*38 + ' '), (203, 'Bar')], 
                                   lines[2:])



