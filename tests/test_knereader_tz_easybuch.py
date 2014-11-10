# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

from datetime import date
from decimal import Decimal

from test_knereader_lxoffice import SampleDataReaderCase

class TestKneReaderTZEasyBuch(SampleDataReaderCase):
    def setUp(self):
        super(TestKneReaderTZEasyBuch, self).setUp('tz_easybuch')
    
    def test_product_abbreviation(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        config = self.reader.get_config()
        self.assertEqual('-TZB', config['product_abbreviation'])
    
    
    def test_transaction_file_line1(self):
        tfile = self.reader.get_file(0)
        lines = tfile.get_posting_lines()
        self.assertEqual(97, len(lines))
        line = lines[0]
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal('23.73'), line.transaction_volume)
        self.assertEqual(1545, line.offsetting_account)
        self.assertEqual('Bank1', line.record_field1)
        self.assertEqual(None, line.record_field2)
        self.assertEqual(date(2008, 1, 1), line.date)
        self.assertEqual(1200, line.account_number)
        self.assertEqual(u'Rest Umsatzsteuer 2007 (wird s', line.posting_text)
