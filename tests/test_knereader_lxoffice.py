# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

from datetime import date
from decimal import Decimal

from tests.test_util import SampleDataReaderCase



class TestKneReaderLxOffice(SampleDataReaderCase):
    def setUp(self):
        super(TestKneReaderLxOffice, self).setUp('lxoffice_transactions')
    
    
    def test_read_global_config(self):
        config = self.reader.get_config()
        self.assertEqual(471156, config['advisor_number'])
        self.assertEqual('Foo Bar', config['advisor_name'])
        
        self.assertEqual(1, config['number_data_files'])
        self.assertEqual(1, config['number_last_data_file'])
        self.assertEqual(1, config['data_carrier_number'])
    
    
    def test_read_control_record(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        tfile = self.reader.get_file(0)
        meta = tfile.get_metadata()
        self.assertEqual(True, meta['do_process'])
        self.assertEqual(1, meta['file_no'])
        self.assertEqual(11, meta['application_number'])
        self.assertEqual('00', meta['name_abbreviation'])
        self.assertEqual(471156, meta['advisor_number'])
        self.assertEqual(42212, meta['client_number'])
        self.assertEqual(11, meta['accounting_number'])
        self.assertEqual(8, meta['accounting_year'])
        self.assertEqual(date(2008, 05, 01), meta['date_start'])
        self.assertEqual(date(2008, 06, 15), meta['date_end'])
        self.assertEqual(1, meta['prima_nota_page'])
        self.assertEqual('0000', meta['password'])
        self.assertEqual(1, meta['number_data_blocks'])
        self.assertEqual('1,4,4,SELF', meta['version_info'])
    
    
    def test_read_data_file(self):
        tfile = self.reader.get_file(0)
        self.assertTrue(tfile.contains_transaction_data())
        meta = tfile.get_metadata()
        self.assertEqual(4, meta['used_general_ledger_account_no_length'])
        self.assertEqual(4, meta['stored_general_ledger_account_no_length'])
    
    
    def test_read_posting_line(self):
        tfile = self.reader.get_file(0)
        lines = tfile.get_posting_lines()
        self.assertEqual(1, len(lines))
        line = lines[0]
        self.assertEqual(Decimal(1250), line.transaction_volume)
        self.assertEqual(1400, line.offsetting_account)
        self.assertEqual('1010', line.record_field1)
        self.assertEqual('15-01-20070', line.record_field2)
        self.assertEqual(date(2008, 06, 13), line.date)
        self.assertEqual(1000, line.account_number)
        self.assertEqual('Wasserspiel GmbH', line.posting_text)
        self.assertEqual('EUR', line.currency_code_transaction_volume)

