# -*- coding: UTF-8 -*-

from decimal import Decimal

from test_knereader_lxoffice import SampleDataReaderCase


class _TestKneReaderDATEVSelfSamples(SampleDataReaderCase):
    def setUp(self):
        super(TestKneReaderDATEVSelfSamples, self).setUp('datev_self', 4)
    
    def test_product_abbreviation(self):
        self.assertEqual(1, self.reader.get_number_of_files())
        tfile = self.reader.get_file(0)
        self.assertEqual("SELF ID: 99999", tfile.get_metadata()['application_info'])
        lines = tfile.get_posting_lines()
        
        line4 = lines[3]
        self.assertEqual(Decimal("832.82"), line4.base_currency_amount)
        self.assertEqual("EUR", line4.base_currency)
        self.assertEqual("USD", line4.currency_code_transaction_volume)
        self.assertEqual(Decimal("1.200740"), line4.exchange_rate)
        
        line8 = lines[7]
        self.assertEqual(230, line8.cash_discount)



