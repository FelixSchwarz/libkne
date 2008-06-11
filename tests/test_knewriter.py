# -*- coding: UTF-8 -*-

import datetime
from decimal import Decimal
import StringIO
import unittest


from libkne import KneWriter, PostingLine


def _default_config():
    config = {}
    config["advisor_number"] = 1234567
    config["advisor_name"] = 'Datev eG'
    config["client_number"] = 42
    
    config["data_carrier_number"] = 1
    config["name_abbreviation"] = "fs"
    config["date_start"] = datetime.date(2004, 02, 04)
    config["date_end"] = datetime.date(2004, 02, 29)
    return config


def _build_kne_writer(config=None, header_fp=None):
    if config == None:
        config = _default_config()
    data_fp = StringIO.StringIO()
    data_fp_builder = lambda x: data_fp
    if header_fp == None:
        header_fp = StringIO.StringIO()
    writer = KneWriter(header_fp=header_fp, data_fp_builder=data_fp_builder,
                       config=config)
    return (writer, data_fp)


def _build_posting_line(**kwargs):
    line = PostingLine()
    line.transaction_volume = -115
    line.offsetting_account = 100010000
    line.record_field1 = "Re526100910"
    line.record_field2 = "150102"
    line.date = datetime.date(day=1, month=1, year=2008)
    line.account_number = 84000000
    line.posting_text = "AR mit UST-Automatikkonto"
    line.currency_code_transaction_volume = "EUR"
    for key in kwargs:
        if hasattr(line, key):
            setattr(line, key, kwargs[key])
    return line

def _default_binary_posting_line(with_ammount=True):
    binary_line = ''
    if with_ammount:
        binary_line = '-11500'
    binary_line += 'a' + '100010000' + '\xbd' + \
                   'Re526100910' + '\x1c' + '\xbe' + '150102' + \
                   '\x1c' + 'd' + '101' + 'e' + '84000000' + '\x1e' + \
                   'AR mit UST-Automatikkonto' + '\x1c' + '\xb3' + \
                   'EUR' + '\x1c' + 'y'
    return binary_line
    

class TestPostingLine(unittest.TestCase):
    
    def setUp(self):
        binary_line = _default_binary_posting_line(with_ammount=False)
        self.posting_line_with_transaction_volume = binary_line
    
    
    def test_negative_transaction_volume(self):
        line = _build_posting_line()
        expected_binary = '-11500' + self.posting_line_with_transaction_volume
        self.assertEqual(expected_binary, line.to_binary())
    
    
    def test_positive_transaction_volume(self):
        line = _build_posting_line(transaction_volume=+4711)
        expected_binary = '+471100' + self.posting_line_with_transaction_volume
        self.assertEqual(expected_binary, line.to_binary())
    
    
    def test_decimal_transaction_volume(self):
        line = _build_posting_line(transaction_volume=Decimal("-43.12"))
        expected_binary = '-4312' + self.posting_line_with_transaction_volume
        #print repr(expected_binary)
        #print repr(line.to_binary())
        self.assertEqual(expected_binary, line.to_binary())
    
    
    def test_invalid_decimal_transaction_volume(self):
        line = _build_posting_line(transaction_volume=Decimal("43.124"))
        self.assertRaises(ValueError, line.to_binary)
    
    
    def test_invalid_characters_in_record_line(self):
        line = _build_posting_line(record_field1='abcödef')
        self.assertRaises(ValueError, line.to_binary)
        
        line = _build_posting_line(record_field2='abcödef')
        self.assertRaises(ValueError, line.to_binary)
    
    
    def test_umlaut_encoding_in_posting_text(self):
        umlauts = u"äöüßÄÖÜ!#\"#$%&"
        line = _build_posting_line(posting_text=umlauts + u'§' + u'€')
        binary_line = '-11500' + 'a' + '100010000' + '\xbd' + \
                      'Re526100910' + '\x1c' + '\xbe' + '150102' + \
                      '\x1c' + 'd' + '101' + 'e' + '84000000' + '\x1e' + \
                      umlauts.encode("CP437") + '\x15' + '\xfe' + '\x1c' + \
                      '\xb3' + 'EUR' + '\x1c' + 'y'
        #print repr(binary_line)
        #print repr(line.to_binary())
        self.assertEqual(binary_line, line.to_binary())
    
    
    def test_invalid_characters_in_posting_text(self):
        line = _build_posting_line(posting_text='á')
        self.assertRaises(ValueError, line.to_binary)
    
    
    def test_date(self):
        line = _build_posting_line(date=datetime.date(2008, 12, 21))
        binary_line = '-11500' + 'a' + '100010000' + '\xbd' + \
                      'Re526100910' + '\x1c' + '\xbe' + '150102' + \
                      '\x1c' + 'd' + '2112' + 'e' + '84000000' + '\x1e' + \
                      'AR mit UST-Automatikkonto' + '\x1c' + '\xb3' + \
                      'EUR' + '\x1c' + 'y'
        #print repr(binary_line)
        #print repr(line.to_binary())
        self.assertEqual(binary_line, line.to_binary())



class TestKneWriting(unittest.TestCase):
    def setUp(self):
        self.header_fp = StringIO.StringIO()
        self.writer, self.data_fp = _build_kne_writer(header_fp=self.header_fp)
    
    
    def _assemble_data(self):
        line = _build_posting_line()
        self.writer.add_posting_line(line)
        self.writer.add_posting_line(line)
        self.writer.finish()
        
        self.header_fp.seek(0)
        self.data_fp.seek(0)
    
    
    def _check_header_file(self, binary_header):
        data_carrier = '001' + '   ' + '1234567' + 'Datev eG ' + ' ' + \
                       '00001' + '00001' + (' ' * 95)
        control_record = 'V' + '00001' + '11' + 'FS' + '1234567' + '00042' + \
                         '000108' + '0000040204' + '290204' + '001' + '    ' + \
                         '00002' + '001' + ' ' + '1' + '1,8,8,lkne    ' + \
                         (' ' * 53)
        self.assertEqual(128, len(control_record))
        expected_binary = data_carrier + control_record
        self.assertEqual(256, len(expected_binary))
        
        #print repr(expected_binary)
        #print repr(binary_header)
        self.assertEqual(expected_binary, binary_header)
    
    
    def _check_complete_feed_line(self, binary_data):
        expected_feed_line = '\x1d' + '\x18' + '1' + '001' + '11' + 'FS' + \
                             '1234567' + '00042' + '000108' + \
                             '040204' + '290204' + '001' + '    ' + \
                             (' ' * 16) + (' ' * 16) + 'y'
        self.assertEqual(80, len(expected_feed_line))
        #print repr(expected_feed_line)
        #print repr(binary_data)
        self.assertEquals(expected_feed_line, binary_data)
        
    
    def _check_version_string(self, binary_data):
        expected_version_string = '\xb5' + '1,8,8,lkne' + '\x1c' + 'y'
        self.assertEqual(13, len(expected_version_string))
        #print repr(expected_version_string)
        #print repr(binary_data)
        self.assertEquals(expected_version_string, binary_data)
    
    
    def _check_posting_line(self, binary_data, start):
        post_line = _default_binary_posting_line()
        end = start + len(post_line)
        binary_line = binary_data[start:end]
        print repr(post_line)
        print repr(binary_line)
        self.assertEqual(post_line, binary_line)
        return end
    
    
    def _check_for_filling(self, binary_data, start, end):
        expected_filling = '\0'*(end-start)
        real_filling = binary_data[start:end]
        print repr(expected_filling)
        print repr(real_filling)
        self.assertEqual(expected_filling, real_filling)
    
    def test_finish(self):
        self._assemble_data()
        binary_header = self.header_fp.read()
        self._check_header_file(binary_header)
 
        binary_data = self.data_fp.read()
        self.assertEqual(0, len(binary_data) % 256)
        self._check_complete_feed_line(binary_data[:80])
        self._check_version_string(binary_data[80:93])
        
        end = self._check_posting_line(binary_data, 93)
        self._check_for_filling(binary_data, end, 256)
        end = self._check_posting_line(binary_data, 256)
        # TODO: Abschluss der Datendatei!
        self._check_for_filling(binary_data, end, 256)

