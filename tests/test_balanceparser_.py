# -*- coding: UTF-8 -*-

from libkne.model import BalanceParser

from tests.test_util import SampleDataReaderCase


class TestBalanceParserLxOffice(SampleDataReaderCase):
    def setUp(self):
        super(TestBalanceParserLxOffice, self).setUp('lxoffice_transactions')
        self.parser = BalanceParser(self.reader)
    
    
    def test_parse_balance(self):
        balances = self.parser.balances()
        self.assertEqual(2, len(balances))
        
        account1000 = balances[0]
        self.assertEqual(1000, account1000.number)
        self.assertEqual(1250, account1000.balance)
        
        account1400 = balances[1]
        self.assertEqual(1400, account1400.number)
        self.assertEqual(-1250, account1400.balance)

