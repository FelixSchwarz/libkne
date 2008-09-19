# -*- coding: UTF-8 -*-

from copy import copy

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
            data_config = copy(self.config)
            data_config['application_number'] = 13
            data_config['accounting_number'] = 189
            new_file = DataFile(data_config, self.version_identifier)
            self.masterdata_files.append(new_file)
        tf = self.masterdata_files[-1]
        assert tf.append_line(line)
    
    
    def append_posting_line(self, line):
        if len(self.transaction_files) == 0:
            data_config = copy(self.config)
            data_config['application_number'] = 11
            new_file = DataFile(data_config, self.version_identifier)
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
        nr_files = 0
        for files in [self.transaction_files, self.masterdata_files]:
            for df in files:
                data_fp = self.data_fp_builder(nr_files)
                data_fp.write(df.to_binary())
                control_records.append(df.build_control_record(nr_files))
                nr_files += 1
        return control_records

