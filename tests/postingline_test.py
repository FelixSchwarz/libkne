# -*- coding: UTF-8 -*-

from datetime import date
import unittest

from libkne import PostingLine



def get_minimal_metadata():
    return dict(stored_general_ledger_account_no_length=4,
                date_start=date(2007, 10, 1), date_end=date(2007, 10, 10))


def build_minimal_postingline():
    metadata = get_minimal_metadata()
    line = PostingLine(metadata)
    line.transaction_volume = -115
    line.offsetting_account = 1000
    line.date = date(day=5, month=10, year=2007)
    line.account_number = 8400
    line.currency_code_transaction_volume = 'EUR'
    return line



class TestPostingline(unittest.TestCase):
    
    def test_write_minimal_posting_line_to_binary(self):
        line = build_minimal_postingline()
        self.assertEqual(['-11500a1000d510e8400\xb3EUR\x1cy'], line.to_binary())
    
    def _get_binary_for_reserved(self, values):
        binary_reserved = ''
        delimiters = [('g', ''), ('\xb0', '\x1c'), ('\xb1', '\x1c'), 
                      ('\xb2', '\x1c'), ('f', ''), ('p', ''), ('q', '')]
        for (value, delimiter) in zip(values, delimiters):
            if value != None:
                binary_reserved += delimiter[0] + str(value) + delimiter[1]
        return binary_reserved
    
    def test_write_reserved_fields_to_binary(self):
        line = build_minimal_postingline()
        reserved_fields = [123456789012, 'abc', 'def', 'ghi', 12345678901, 
                           123, 123456789012]
        line.reserved_fields = list(reserved_fields)
        binary_reserved = self._get_binary_for_reserved(reserved_fields)
        binary_line = '-11500a1000d510e8400\xb3EUR\x1c' + binary_reserved + 'y'
        self.assertEqual([binary_line], line.to_binary())
    
    def test_write_only_some_reserved_fields_to_binary(self):
        line = build_minimal_postingline()
        reserved_fields = [None, None, 'def', None, None, None, None]
        line.reserved_fields = list(reserved_fields)
        binary_line = '-11500a1000d510e8400\xb3EUR\x1c' + '\xb1def\x1c' + 'y'
        self.assertEqual([binary_line], line.to_binary())
    
    def test_parse_reserved_fields(self):
        reserved_fields = [123456789012, 'abc', 'def', 'ghi', 12345678901, 
                           123, 123456789012]
        binary_reserved = self._get_binary_for_reserved(reserved_fields)
        binary_line = '-11500a1000d510e8400\xb3EUR\x1c' + binary_reserved + 'y'
        
        parsed_line, end_index = \
            PostingLine.from_binary(binary_line, 0, get_minimal_metadata())
        self.assertEqual(reserved_fields, parsed_line.reserved_fields)
    
    def test_parse_only_some_reserved_fields(self):
        reserved_fields = [None, 'abc', None, 'ghi', None, None, None]
        binary_reserved = self._get_binary_for_reserved(reserved_fields)
        binary_line = '-11500a1000d510e8400\xb3EUR\x1c' + binary_reserved + 'y'
        
        parsed_line, end_index = \
            PostingLine.from_binary(binary_line, 0, get_minimal_metadata())
        self.assertEqual(reserved_fields, parsed_line.reserved_fields)

