# -*- coding: UTF-8 -*-

from transactionfile import TransactionFile

__all__ = ['TransactionManager']

class TransactionManager(object):
    
    def __init__(self, config, version_identifier, data_fp_builder):
        self.config = config
        self.version_identifier = version_identifier
        self.data_fp_builder = data_fp_builder
        
        self.transaction_files = []
    
    
    def append_posting_line(self, line):
        if self.transaction_files == []:
            new_file = TransactionFile(self.config, self.version_identifier)
            self.transaction_files.append(new_file)
        tf = self.transaction_files[-1]
        assert tf.append_posting_line(line)
    
    
    def finish(self):
        '''Write all transaction files using the data_fp_builder. No 
        transaction data may be appended after calling finish (although 
        finish() itself may be called multiple times.
        Return a list of control records. 
        '''
        control_records = []
        for i, tf in enumerate(self.transaction_files):
            data_fp = self.data_fp_builder(i)
            data_fp.write(tf.to_binary())
            control_records.append(tf.build_control_record())
        return control_records

