# -*- coding: UTF-8 -*-

from libkne import DataLine

from test_knereader_lxoffice import SampleDataReaderCase


class TestKneReaderMasterDataMMS(SampleDataReaderCase):
    def setUp(self):
        super(TestKneReaderMasterDataMMS, self).setUp('mms_bilanz_addresses')
    
    def test_product_abbreviation(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        tfile = self.reader.get_file(0)
        self.assertEqual('SELF ID: 15540', tfile.get_metadata()['application_info'])
        config = self.reader.get_config()
        self.assertEqual('SELF', config['product_abbreviation'])
    
    
    def test_master_data(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        tfile = self.reader.get_file(0)
        data_lines = tfile.get_master_data_lines()
        self.assertEqual(11, len(data_lines))
        self.assertEqual(DataLine(101, '1'), data_lines[0])
        self.assertEqual(DataLine(102, '10000'), data_lines[1])
        self.assertEqual(DataLine(103, 'Evil'), data_lines[2])
        self.assertEqual(DataLine(203, 'aka Big Boss'), data_lines[3])
        self.assertEqual(DataLine(108, 'Wall Street 123'), data_lines[4])
        self.assertEqual(DataLine(106, '4711'), data_lines[5])
        self.assertEqual(DataLine(107, 'New York'), data_lines[6])
        self.assertEqual(DataLine(500, 'DE123456789'), data_lines[7])
        self.assertEqual(DataLine(130, 'Berliner Sparkasse'), data_lines[8])
        self.assertEqual(DataLine(132, '123456789'), data_lines[9])
        self.assertEqual(DataLine(133, '50050201'), data_lines[10])



