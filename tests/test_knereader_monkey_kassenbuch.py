# -*- coding: UTF-8 -*-

from test_knereader_lxoffice import SampleDataReaderCase


class TestKneReaderMonkeyKassenbuch(SampleDataReaderCase):
    def setUp(self):
        datadir = 'monkey_kassenbuch_transactions'
        super(TestKneReaderMonkeyKassenbuch, self).setUp(datadir)
    
    def test_product_abbreviation(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        config = self.reader.get_config()
        self.assertEqual('MKEY', config['product_abbreviation'])



class TestKneReaderMonkeyKassenbuchAccountLabels(SampleDataReaderCase):
    def setUp(self):
        datafile = 'monkey_kassenbuch_account_labels'
        super(TestKneReaderMonkeyKassenbuchAccountLabels, self).setUp(datafile)
    
    def test_account_labels(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        dfile = self.reader.get_file(0)
        data_lines = dfile.get_master_data_lines()
        self.assertEqual(286, len(data_lines))
        line2 = data_lines[1]
        self.assertEqual(65, line2.key)
        self.assertEqual(u"Unbebaute Grundstücke", line2.text)


