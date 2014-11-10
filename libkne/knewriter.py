# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

import datetime

from transactionmanager import TransactionManager
from util import product_abbreviation

__all__ = ['KneWriter']


class KneWriter(object):
    
    def __init__(self, config=None, header_fp=None, data_fp_builder=None):
        '''header_fp is a file-like object which will be used to store the KNE
        header. data_fp_builder is a callable that will return a file-like 
        object when called with the number of previously retrieved fp as a an
        argument. These file-like objects will be used to store the data items 
        (transaction data or master data).'''
        self.header_fp = header_fp
        self.data_fp_builder = data_fp_builder
        self.number_data_files = 0
        
        self.posting_fp = None
        self.posting_fp_feed_written = False
        self.posting_fp_version_info_written = False
        
        self.control_records = []
        self.config = self._build_config(config)
        
        version_info = self.get_version_identifier()
        self.transaction_manager = TransactionManager(self.config, version_info,
                                                      data_fp_builder)
    
    
    def _build_config(self, cfg):
        config = {}
        if cfg != None:
            config.update(cfg)
        config.setdefault('data_carrier_number', 0)
        assert int(config['data_carrier_number']) in range(0,999)
        config.setdefault('gl_account_no_length_data', 8)
        config.setdefault('gl_account_no_length_coredata', 8)
        gl_account_no_length_data = config['gl_account_no_length_data']
        gl_account_no_length_coredata = config['gl_account_no_length_coredata']
        assert gl_account_no_length_data in range(4,9)
        assert gl_account_no_length_coredata in range(4,9)
        assert not (gl_account_no_length_data < gl_account_no_length_coredata)
        
        if config.get('advisor_name') != None:
            config['advisor_name'] = '% -9s' % config['advisor_name']
            assert len(config['advisor_name']) == 9
        
        assert int(config['advisor_number']) > 0
        assert len(str(config['advisor_number'])) in range(1,8)
        config['advisor_number'] = '%07d' % int(config['advisor_number'])
        
        assert int(config['client_number']) > 0
        assert len(str(config['client_number'])) in range(1,6)
        config['client_number'] = '%05d' % int(config['client_number'])
        
        assert len(config['name_abbreviation']) == 2
        config['name_abbreviation'] = config['name_abbreviation'].upper()
        
        config.setdefault('accounting_number', 1)
        assert len(str(config['accounting_number'])) in range(1,5)
        config['accounting_number'] = '%04d' % int(config['accounting_number'])
        
        config.setdefault('accounting_year', datetime.date.today().year)
        assert len(str(config['accounting_year'])) == 4
        
        config.setdefault('password', '    ')
        assert len(config['password']) == 4
        
        assert config['date_start'] != None
        assert config['date_end'] != None
        assert config['date_start'] <= config['date_end']
        
        config.setdefault('prima_nota_page', 1)
        config['prima_nota_page'] = '%03d' % int(config['prima_nota_page'])
        assert len(config['prima_nota_page']) == 3
        
        # should not be set from the user as this are more or less constants
        config.setdefault('version_complete_feed_line', '1')
        config.setdefault('application_number', '11') # Fibu/OPOS transaction data
        
        config.setdefault('application_info', ' ' * 16)
        config['application_info'] ='% -16s' % config['application_info']
        assert len(config['application_info']) == 16
        
        config.setdefault('input_info', ' ' * 16)
        config['input_info'] ='% -16s' % config['input_info']
        assert len(config['input_info']) == 16
        
        return config
    
    
    def get_version_identifier(self):
        bin_versionid = '1,'
        bin_versionid += str(self.config['gl_account_no_length_data'])
        bin_versionid += ','
        bin_versionid += str(self.config['gl_account_no_length_coredata'])
        bin_versionid += ','
        assert len(product_abbreviation) == 4
        assert str(product_abbreviation) == product_abbreviation
        bin_versionid += str(product_abbreviation)
        return bin_versionid
    
    
    def _build_data_carrier_header(self, number_of_files):
        bin_line = '%03d' % self.config['data_carrier_number']
        bin_line += '   '
        bin_line += self.config['advisor_number']
        bin_line += self.config['advisor_name']
        bin_line += ' '
        bin_line += '%05d' % number_of_files
        bin_line += '%05d' % number_of_files
        bin_line += (' ' * 95)
        return bin_line
    
    
    def _build_control_record_header(self, control_records):
        binary = ''
        version_info = self.get_version_identifier()
        for cr in control_records:
            binary += cr.to_binary(version_info)
        return binary
    
    
    def _build_control_header(self, control_records):
        number_of_files = len(control_records)
        binary = self._build_data_carrier_header(number_of_files)
        binary += self._build_control_record_header(control_records)
        return binary
    
    
    def add_posting_line(self, line):
        self.transaction_manager.append_posting_line(line)
    
    
    def add_posting_lines(self, lines):
        for line in lines:
            self.add_posting_line(line)
    
    
    def add_masterdata_line(self, line):
        self.transaction_manager.append_masterdata_line(line)
    
    
    def add_masterdata_lines(self, lines):
        for line in lines:
            self.add_masterdata_line(line)
    
    
    def finish(self):
        '''Write all data to the given file-like objects and generate the header
        file contents.'''
        control_records = self.transaction_manager.finish()
        header_string = self._build_control_header(control_records)
        self.header_fp.write(header_string)

