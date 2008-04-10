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


class TestPostingLine(unittest.TestCase):
    
    def setUp(self):
        binary_line = 'a' + '100010000' + '\xbd' + \
                      'Re526100910' + '\x1c' + '\xbe' + '150102' + \
                      '\x1c' + 'd' + '101' + 'e' + '84000000' + '\x1e' + \
                      'AR mit UST-Automatikkonto' + '\x1c' + '\xb3' + \
                      'EUR' + '\x1c' + 'y'
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
        print repr(expected_binary)
        print repr(line.to_binary())
        self.assertEqual(expected_binary, line.to_binary())
    
    
    def test_invalid_decimal_transaction_volume(self):
        line = _build_posting_line(transaction_volume=Decimal("43.124"))
        try:
            line.to_binary()
            self.fail("Decimal values with more than two decimal places " + \
                      "must be rejected!")
        except ValueError:
            pass
        expected_binary = '-4312' + self.posting_line_with_transaction_volume
    
    
    
    # Float
    # Datum vierstellig
    # Umlaute im Betreff



#class TestKneDataCarrierHeader(unittest.TestCase):
#    def test_write_header(self):
#        header_fp = StringIO.StringIO()
#        config = _default_config()
#        config["advisor_number"] = 28167
#        self.writer, self.data_fp = _build_kne_writer(config=config, 
#                                                      header_fp=header_fp)
#        self.writer.number_data_files = 1
#        self.writer.write_data_carrier_header()
#        header_fp.seek(0)
#        written_data = header_fp.read()
#        binary_data = '001' + '   ' + '0028167' + 'Datev eG ' + ' ' + \
#                      '00001' + '00001' + (' ' * 95)
#        self.assertEqual(binary_data, written_data)
#        
#

#class TestKneCompleteFeedLine(unittest.TestCase):
#    def setUp(self):
#        config = _default_config()
#        config.update({"name_abbreviation": "ab", "advisor_number": 28167,
#                       "client_number": 1, "accounting_year": 2007, 
#                       "date_start": datetime.date(2007, 1, 1),
#                       "date_end": datetime.date(2007, 1, 31),
#                       "application_info": "SELF ID: 99999"})
#        self.writer, self.data_fp = _build_kne_writer(config=config)
#    
#    
#    def test_write(self):
#        self.writer.check_posting_fp()
#        # will call write_complete_feed_line
#        self.data_fp.seek(0)
#        written_data = self.data_fp.read()
#        expected_binstring = '\x1d' + '\x18' + '100111AB002816' + \
#                             '7000010001070101' + '07310107001' + \
#                             '    SELF ID: 99999   ' + '               ' + 'y'
#        print repr(expected_binstring)
#        print repr(written_data)
#        self.assertEquals(expected_binstring, written_data)
#

#class TestKneVersionString(unittest.TestCase):
#    def setUp(self):
#        self.writer, self.data_fp = _build_kne_writer()
#    
#    
#    def _get_written_version_info(self):
#        length_version_info = 13
#        
#        current_position = self.data_fp.tell()
#        assert current_position >= length_version_info
#        self.data_fp.seek(current_position - length_version_info)
#        return self.data_fp.read()
#    
#    
#    def test_versionstring(self):
#        self.writer.write_versioninfo_for_transaction_data()
#        written_data = self._get_written_version_info()
#        expected_binstring = '\xb5' + '1,8,8,lkne' + '\x1c' + 'y'
#        self.assertEquals(expected_binstring, written_data)
#    
#    
#    def test_only_a_single_versioninfo(self):
#        self.writer.write_versioninfo_for_transaction_data()
#        try:
#            self.writer.write_versioninfo_for_transaction_data()
#        except:
#            written_data = self._get_written_version_info()
#            self.assertEquals(13, len(written_data))
#        else: 
#            self.fail("Only a single version info header must be written!")




class TestKneWriting(unittest.TestCase):
    def setUp(self):
        self.header_fp = StringIO.StringIO()
        self.writer, self.data_fp = _build_kne_writer(header_fp=self.header_fp)
        
    def test_finish(self):
        line = _build_posting_line()
        #writer.write_data_carrier_header()
        self.writer.add_posting_line(line)
        self.writer.finish()
        
        self.header_fp.seek(0)
        self.data_fp.seek(0)
        binary_header = self.header_fp.read()
 
        data_carrier = '001' + '   ' + '1234567' + 'Datev eG ' + ' ' + \
                       '00001' + '00001' + (' ' * 95)
        control_record = 'V' + '00001' + '11' + 'FS' + '1234567' + '00042' + \
                         '000108' + '0000040204' + '290204' + '001' + '    ' + \
                         '00001' + '001' + ' ' + '1' + '1,8,8,lkne    ' + \
                         (' ' * 53)
        self.assertEqual(128, len(control_record))
        expected_binary = data_carrier + control_record
        print repr(expected_binary)
        print repr(binary_header)
        self.assertEqual(256, len(binary_header))
        self.assertEqual(expected_binary, binary_header)

        binary_data = self.data_fp.read()
        # length of binary_data
        # contents of header/data

    
