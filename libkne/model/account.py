# -*- coding: UTF-8 -*-


__all__ = ["KNEAccount"]

class KNEAccount(object):
    def __init__(self, account_number, balance=None):
        self.number = account_number
        self.label = None
        self.balance = balance

