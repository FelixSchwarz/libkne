# -*- coding: UTF-8 -*-

import datetime
import StringIO
import unittest


from libkne import KneWriter, PostingLine


def _default_config():
    config = {}
    config["advisor_number"] = 1234567
    config["client_number"] = 42
    
    config["data_carrier_number"] = 1
    config["name_abbreviation"] = "fs"
    config["date_start"] = datetime.date(2004, 02, 04)
    config["date_end"] = datetime.date(2004, 02, 29)
    return config


def _build_kne_writer(config=None):
    if config == None:
        config = _default_config()
    data_fp = StringIO.StringIO()
    data_fp_builder = lambda x: data_fp
    h_buffer = StringIO.StringIO()
    writer = KneWriter(header_fp=h_buffer, data_fp_builder=data_fp_builder,
                       config=config)
    return (writer, data_fp)


class TestKneCompleteFeedLine(unittest.TestCase):
    def setUp(self):
        config = _default_config()
        config.update({"name_abbreviation": "ab", "advisor_number": 28167,
                       "client_number": 1, "accounting_year": 2007, 
                       "date_start": datetime.date(2007, 1, 1),
                       "date_end": datetime.date(2007, 1, 31),
                       "application_info": "SELF ID: 99999"})
        self.writer, self.data_fp = _build_kne_writer(config=config)
    
    
    def test_write(self):
        self.writer.check_posting_fp()
        # will call write_complete_feed_line
        self.data_fp.seek(0)
        written_data = self.data_fp.read()
        expected_binstring = '\x1d' + '\x18' + '100111AB002816' + \
                             '7000010001070101' + '07310107001' + \
                             '    SELF ID: 99999   ' + '               ' + 'y'
        print repr(expected_binstring)
        print repr(written_data)
        self.assertEquals(expected_binstring, written_data)


class TestKneVersionString(unittest.TestCase):
    def setUp(self):
        self.writer, self.data_fp = _build_kne_writer()
    
    
    def _get_written_version_info(self):
        length_version_info = 13
        
        current_position = self.data_fp.tell()
        assert current_position >= length_version_info
        self.data_fp.seek(current_position - length_version_info)
        return self.data_fp.read()
    
    
    def test_versionstring(self):
        self.writer.write_versioninfo_for_transaction_data()
        written_data = self._get_written_version_info()
        expected_binstring = '\xb5' + '1,8,8,lkne' + '\x1c' + 'y'
        self.assertEquals(expected_binstring, written_data)
    
    
    def test_only_a_single_versioninfo(self):
        self.writer.write_versioninfo_for_transaction_data()
        try:
            self.writer.write_versioninfo_for_transaction_data()
        except:
            written_data = self._get_written_version_info()
            self.assertEquals(13, len(written_data))
        else: 
            self.fail("Only a single version info header must be written!")


class TestPostingLine(unittest.TestCase):
    def test_to_binary_negative_transaction_volume(self):
        line = PostingLine()
        line.transaction_volume = -115
        line.offsetting_account = 100010000
        line.record_field1 = "Re526100910"
        line.record_field2 = "150102"
        line.date = datetime.date(day=1, month=1, year=2008)
        line.account_number = 84000000
        line.posting_text = "AR mit UST-Automatikkonto"
        line.currency_code_transaction_volume = "EUR"
        
        expected_binary = '-11500' + 'a' + '100010000' + '\xbd' + \
                          'Re526100910' + '\x1c' + '\xbe' + '150102' + \
                          '\x1c' + 'd' + '101' + 'e' + '84000000' + '\x1e' + \
                          'AR mit UST-Automatikkonto' + '\x1c' + '\xb3' + \
                          'EUR' + '\x1c' + 'y'
        self.assertEqual(expected_binary, line.to_binary())
    
    #self.posting_fp_feed_written
    
    # Decimal
    # Float
    # Positive werte
    # Datum vierstellig
    # Umlaute im Betreff

