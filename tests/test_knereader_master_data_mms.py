# -*- coding: UTF-8 -*-

from datetime import date
from decimal import Decimal
import os
import unittest

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



