# -*- coding: UTF-8 -*-

from datafile import DataFile

__all__ = ['TransactionManager']

class TransactionManager(object):
    
    def __init__(self, config, version_identifier, data_fp_builder):
        self.config = config
        self.version_identifier = version_identifier
        self.data_fp_builder = data_fp_builder
        
        self.transaction_files = []
        self.masterdata_files = []
    
    
    def append_masterdata_line(self, line):
        if len(self.masterdata_files) == 0:
            new_file = DataFile(self.config, self.version_identifier)
            self.masterdata_files.append(new_file)
        tf = self.masterdata_files[-1]
        assert tf.append_line(line)
    
    
    def append_posting_line(self, line):
        if len(self.transaction_files) == 0:
            new_file = DataFile(self.config, self.version_identifier)
            self.transaction_files.append(new_file)
        tf = self.transaction_files[-1]
        assert tf.append_line(line)
    
    
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

