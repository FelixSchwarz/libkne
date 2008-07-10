# -*- coding: UTF-8 -*-
"""Groups transaction information and computes the account balance out of it."""

from operator import attrgetter

from libkne.model.account import KNEAccount

__all__ = ["BalanceParser"]

class BalanceParser(object):
    
    def __init__(self, reader):
        self.reader = reader
    
    
    def _process_file(self, accounts, datafile):
        if datafile.contains_transaction_data():
            for line in datafile.get_posting_lines():
                self._process_line(accounts, line)
    
    
    def _create_accounts_if_necessary(self, accounts, line):
        for account_nr in [line.offsetting_account, line.account_number]:
            if account_nr not in accounts:
                accounts[account_nr] =  KNEAccount(account_nr, balance=0)
    
    
    def _process_line(self, accounts, line):
        self._create_accounts_if_necessary(accounts, line)
        amount = line.transaction_volume
        accounts[line.account_number].balance += amount
        accounts[line.offsetting_account].balance -= amount
    
    
    def _serialize_account_list(self, accounts):
        accountlist = accounts.values()
        accountlist.sort(key=attrgetter('number'))
        return accountlist
    
    
    def balances(self):
        accounts = {}
        for i in range(self.reader.get_number_of_files()):
            self._process_file(accounts, self.reader.get_file(i))
        return self._serialize_account_list(accounts)

