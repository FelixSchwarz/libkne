# -*- coding: UTF-8 -*-

from datetime import date
from decimal import Decimal

from test_knereader_lxoffice import SampleDataReaderCase


class TestKneReaderDATEVSelfSamples(SampleDataReaderCase):
    def setUp(self):
        super(TestKneReaderDATEVSelfSamples, self).setUp('datev_self', 4)
    
    
    def test_product_abbreviation(self):
        self.assertEqual(4, self.reader.get_number_of_files())
        tfile = self.reader.get_file(0)
        self.assertEqual('SELF ID: 99999', tfile.get_metadata()['application_info'])
    
    
    def _get_line(self, file_index, line_index, nr_lines):
        tfile = self.reader.get_file(file_index)
        self.assertTrue(tfile.contains_transaction_data())
        lines = tfile.get_posting_lines()
        self.assertEqual(nr_lines, len(lines))
        return lines[line_index]
    
    
    def _get_transaction_line(self, line_index):
        return self._get_line(0, line_index, 8)
    
    
    def test_transaction_file_line1(self):
        line = self._get_transaction_line(0)
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(-115), line.transaction_volume)
        self.assertEqual(100010000, line.offsetting_account)
        self.assertEqual('Re526100910', line.record_field1)
        self.assertEqual('150102', line.record_field2)
        self.assertEqual(date(2007, 1, 1), line.date)
        self.assertEqual(84000000, line.account_number)
        self.assertEqual(u'AR mit UST-Automatikkonto', line.posting_text)
    
    
    def test_transaction_file_line2(self):
        line = self._get_transaction_line(1)
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(34500), line.transaction_volume)
        self.assertEqual(84000000, line.offsetting_account)
        self.assertEqual('Re526100910', line.record_field1)
        self.assertEqual('150102', line.record_field2)
        self.assertEqual(date(2007, 1, 1), line.date)
        self.assertEqual(100010000, line.account_number)
        self.assertEqual(u'AR mit UST-Automatikkonto', line.posting_text)
    
    
    def test_transaction_file_line3(self):
        line = self._get_transaction_line(2)
        self.assertEqual('USD', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(1000), line.transaction_volume)
        self.assertEqual(100020000, line.offsetting_account)
        self.assertEqual('Re527100910', line.record_field1)
        self.assertEqual(None, line.record_field2)
        self.assertEqual(date(2007, 1, 15), line.date)
        self.assertEqual(12000000, line.account_number)
        self.assertEqual(u'Zahlung mit Fremdwährung', line.posting_text)
        self.assertEqual(Decimal('832.82'), line.base_currency_amount)
        self.assertEqual('EUR', line.base_currency)
        self.assertEqual(Decimal('1.200740'), line.exchange_rate)
    
    
    def test_transaction_file_line4(self):
        line = self._get_transaction_line(3)
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(-2300), line.transaction_volume)
        self.assertEqual(9, line.posting_key)
        self.assertEqual(32000000, line.offsetting_account)
        self.assertEqual('1289200010', line.record_field1)
        self.assertEqual('210202', line.record_field2)
        self.assertEqual(date(2007, 1, 21), line.date)
        self.assertEqual(700010000, line.account_number)
        self.assertEqual(u'ER mit UST-Schlüssel', line.posting_text)
    
    
    def test_transaction_file_line5(self):
        line = self._get_transaction_line(4)
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(3000), line.transaction_volume)
        self.assertEqual(82000000, line.offsetting_account)
        self.assertEqual('528200010', line.record_field1)
        self.assertEqual(None, line.record_field2)
        self.assertEqual(date(2007, 1, 24), line.date)
        self.assertEqual(82490000, line.account_number)
        self.assertEqual(u'Aufteilung auf Warengruppe 1', line.posting_text)
    
    
    def test_transaction_file_line6(self):
        line = self._get_transaction_line(5)
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(2000), line.transaction_volume)
        self.assertEqual(82100000, line.offsetting_account)
        self.assertEqual('528200010', line.record_field1)
        self.assertEqual(None, line.record_field2)
        self.assertEqual(date(2007, 1, 24), line.date)
        self.assertEqual(82490000, line.account_number)
        self.assertEqual(u'Aufteilung auf Warengruppe 2', line.posting_text)
    
    
    def test_transaction_file_line7(self):
        line = self._get_transaction_line(6)
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(1000), line.transaction_volume)
        self.assertEqual(82200000, line.offsetting_account)
        self.assertEqual('528200010', line.record_field1)
        self.assertEqual(None, line.record_field2)
        self.assertEqual(date(2007, 1, 24), line.date)
        self.assertEqual(82490000, line.account_number)
        self.assertEqual(u'Aufteilung auf Warengruppe 3', line.posting_text)
    
    
    def test_transaction_file_line8(self):
        line = self._get_transaction_line(7)
        self.assertEqual('EUR', line.currency_code_transaction_volume)
        self.assertEqual(Decimal(11270), line.transaction_volume)
        self.assertEqual(700020000, line.offsetting_account)
        self.assertEqual('4711', line.record_field1)
        self.assertEqual(None, line.record_field2)
        self.assertEqual(date(2007, 1, 29), line.date)
        self.assertEqual(12000000, line.account_number)
        self.assertEqual(u'Lieferantenzahlg. mit Skonto', line.posting_text)
        self.assertEqual(230, line.cash_discount)
    
    
    def test_addresses(self):
        dfile = self.reader.get_file(1)
        data_lines = dfile.get_master_data_lines()
        self.assertEqual(65, len(data_lines))
        line = data_lines[6]
        self.assertEqual(u"Straße-Beispiel", line.text)
    
    
    def test_account_labels(self):
        dfile = self.reader.get_file(2)
        data_lines = dfile.get_master_data_lines()
        self.assertEqual(2, len(data_lines))
        self.assertEqual(12010000, data_lines[0].key)
        self.assertEqual(u"Hausbank", data_lines[0].text)
        self.assertEqual(82990000, data_lines[1].key)
        self.assertEqual(u"Verrechnungskonto Erlöse A", data_lines[1].text)
    
    
    def test_payment_conditions(self):
        dfile = self.reader.get_file(3)
        data_lines = dfile.get_master_data_lines()
        self.assertEqual(35, len(data_lines))
        self.assertEqual(801, data_lines[2].key)
        self.assertEqual(u'30 Tage Netto, 7 Tage 3%, 14 Tage 1,5%', 
                         data_lines[2].text)

