# -*- coding: UTF-8 -*-

import unittest

from libkne.model import KNEAddress


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



