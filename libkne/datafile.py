# -*- coding: UTF-8 -*-

import math
import re
import warnings

from libkne.controlrecord import ControlRecord
from libkne.custom_info_record import CustomInfoRecord
from libkne.data_line import DataLine
from libkne.postingline import PostingLine
from libkne.util import assert_match, assert_true, parse_short_date, \
    _short_date, parse_number, parse_string, APPLICATION_NUMBER_TRANSACTION_DATA

__all__ = ['DataFile']


class DataFile(object):
    
    def __init__(self, config, version_identifier=None):
        self.config = config
        self.binary_info = None
        
        transaction_code = str(APPLICATION_NUMBER_TRANSACTION_DATA)
        app_nr = str(config.get('application_number', transaction_code))
        config['application_number'] = app_nr
        is_transaction_data  = (app_nr == transaction_code)
        self.contains_transaction_lines = is_transaction_data
        self.version_identifier = version_identifier
        
        self.lines = []
        self.cr = None
        
        self.open_for_additions = True
        self.number_of_blocks = None
    
    
    def _client_total(self):
        client_sum_total = 0
        for line in self.lines:
            client_sum_total += line.transaction_volume
        
        if client_sum_total > 0:
            bin_total = 'x'
        else:
            bin_total = 'w'
        int_total = abs(int(100 * client_sum_total))
        
        bin_total += '%014d' % int_total 
        bin_total += 'y' + 'z'
        return bin_total
    
    
    def _get_complete_feed_line(self):
        start_feed_line = '\x1d'
        new_feed = '\x18'
        
        bin_line = start_feed_line + new_feed
        bin_line += self.config['version_complete_feed_line']
        bin_line += '%03d' % self.config['data_carrier_number']
        bin_line += self.config['application_number']
        bin_line += self.config['name_abbreviation']
        bin_line += self.config['advisor_number']
        bin_line += self.config['client_number']
        year2k = str(self.config['accounting_year'])[2:]
        bin_line += self.config['accounting_number'] + year2k
        bin_line += _short_date(self.config['date_start'])
        bin_line += _short_date(self.config['date_end'])
        bin_line += self.config['prima_nota_page']
        bin_line += self.config['password']
        bin_line += self.config['application_info']
        bin_line += self.config['input_info']
        bin_line += 'y'
        assert len(bin_line) == 80
        return bin_line
    
    
    def _get_short_feed_line(self):
        start_feed_line = '\x1d'
        new_feed = '\x18'
        
        bin_line = start_feed_line + new_feed
        bin_line += self.config['version_complete_feed_line']
        bin_line += '%03d' % self.config['data_carrier_number']
        bin_line += self.config['application_number']
        bin_line += self.config['name_abbreviation']
        bin_line += self.config['advisor_number']
        bin_line += self.config['client_number']
        accounting_nr = '%04d' % int(self.config['accounting_number'])
        bin_line += accounting_nr + str(self.config['accounting_year'])[2:]
        bin_line += self.config['password']
        bin_line += self.config['application_info']
        bin_line += self.config['input_info']
        bin_line += 'y'
        assert len(bin_line) == 65
        return bin_line
    
    
    def _get_number_of_blocks(self):
        number_of_bytes = len(self.binary_info)
        number_of_blocks = int(math.ceil(float(number_of_bytes) / 256))
        assert len(str(number_of_blocks)) <= 5
        return number_of_blocks
    
    
    def _get_versioninfo_for_transaction_data(self, version_identifier):
        bin_versioninfo = '\xb5'
        # TODO Sachkontonummern-Laenge ev. separat?
        bin_versioninfo += version_identifier
        bin_versioninfo += '\x1c' + 'y'
        assert len(bin_versioninfo) == 13
        return bin_versioninfo
    
    
    def _get_versioninfo_for_masterdata(self, version_identifier):
        bin_versioninfo = '\xb6'
        # TODO Sachkontonummern-Laenge ev. separat?
        bin_versioninfo += version_identifier
        bin_versioninfo += '\x1c' + 'y'
        assert len(bin_versioninfo) == 13
        return bin_versioninfo
    
    
    def append_line(self, line):
        '''Append a new line to this file (only if to_binary() was not called 
        before on this file!). Return True if the line was appended 
        successfully else False. If False, no more lines can be appended to 
        this file.
        If this file contains transaction data and the new line belongs to 
        another financial year, a ValueError is raised.'''
        assert_true(self.open_for_additions)
        if self.contains_transaction_data():
            assert_true(self.may_add_transactions_for(line.date))
            date_start = self.config['date_start']
            if (date_start == None) or (date_start > line.date):
                self.config['date_start'] = line.date
            date_end = self.config['date_end']
            if (date_end == None) or (date_end < line.date):
                self.config['date_end'] = line.date
            
            # Short feed line must contain the same year as the transaction data
            self.config['accounting_year'] = line.date.year
        
        self.lines.append(line)
        return True
    
    
    def build_control_record(self, nr_files):
        cr = ControlRecord()
        cr.file_no = nr_files + 1
        cr.application_number = self.config['application_number']
        cr.name_abbreviation = self.config['name_abbreviation']
        cr.advisor_number = self.config['advisor_number']
        cr.client_number = self.config['client_number']
        cr.accounting_number = self.config['accounting_number']
        cr.accounting_year = self.config['accounting_year']
        cr.date_start = self.config['date_start']
        cr.date_end = self.config['date_end']
        cr.prima_nota_page = self.config['prima_nota_page']
        cr.password = self.config['password']
        
        cr.number_of_blocks = self.number_of_blocks
        self.cr = cr
        return cr
    
    
    def contains_transaction_data(self):
        result = self.contains_transaction_lines
        if hasattr(self, 'cr') and self.cr != None:
            result = self.cr.describes_transaction_data()
        return result
    
    
    def _compute_number_of_fill_bytes(self):
        number_of_bytes = len(self.binary_info)
        missing_bytes = 256 - (number_of_bytes % 256)
        return missing_bytes
    
    
    def _add_fill_bytes_at_file_end(self):
        missing_bytes = self._compute_number_of_fill_bytes()
        if missing_bytes > 0:
            self.binary_info += '\x00' * missing_bytes
    
    
    def _insert_fill_bytes(self, binary_line):
        number_fill_bytes = 6
        blocks_used = len(self.binary_info) / 256 + 1
        end_block_index = blocks_used * 256
        free_bytes_in_block = end_block_index - number_fill_bytes \
                                  - len(self.binary_info)
        if free_bytes_in_block < len(binary_line):
            binary_line = binary_line[:free_bytes_in_block] + \
                          ('\x00' * number_fill_bytes) + \
                          binary_line[free_bytes_in_block:]
        return binary_line
    
    
    def finish(self):
        if self.open_for_additions:
            for line in self.lines:
                for posting_line in line.to_binary():
                    self.binary_info += self._insert_fill_bytes(posting_line)
            if self.contains_transaction_data():
                self.binary_info += self._client_total()
            else:
                self.binary_info += 'z'
            self._add_fill_bytes_at_file_end()
            self.open_for_additions = False
    
    
    def _remove_fill_bytes(self, binary_data, number_data_blocks):
        filtered_data = binary_data
        for i in range(number_data_blocks, 0, - 1):
            end_index = 256 * i - 1
            assert ('\x00' * 6) == filtered_data[end_index-5:end_index+1]
            start_index = end_index
            while filtered_data[start_index] == '\x00':
                start_index -= 1
            filtered_data = filtered_data[:start_index+1] + filtered_data[end_index+1:]
        return filtered_data
    
    
    def _check_feed_line(self, metadata, binary_data):
        assert len(binary_data) == 80
        assert binary_data[0] == '\x1d', repr(binary_data[0])
        assert binary_data[1] == '\x18'
        assert binary_data[2] == '1'
        data_carrier_number = self.config['data_carrier_number']
        err_msg = ('%d != %s' % (data_carrier_number, repr(binary_data[3:6])))
        assert data_carrier_number == int(binary_data[3:6]), err_msg
        application_number = int(binary_data[6:8])
        application_number_cr = self.cr.parsed_data()['application_number']
        assert application_number == application_number_cr, application_number
        assert metadata['name_abbreviation'] == binary_data[8:10]
        assert metadata['advisor_number'] == int(binary_data[10:17])
        assert metadata['client_number'] == int(binary_data[17:22])
        assert metadata['accounting_number'] == int(binary_data[22:26])
        assert metadata['accounting_year'] == int(binary_data[26:28])
        if self.cr.describes_transaction_data():
            date_start = parse_short_date(binary_data[28:34])
            assert metadata['date_start'] == date_start
            date_end = parse_short_date(binary_data[34:40])
            assert metadata['date_end'] == date_end
            assert metadata['prima_nota_page'] == int(binary_data[40:43])
            index = 43
        else:
            index = 28
        assert metadata['password'] == binary_data[index:index+4]
        metadata['application_info'] = binary_data[index+4:index+20].strip()
        metadata['input_info'] = binary_data[index+20:index+36].strip()
        assert 'y' == binary_data[index+36]
        return index + 36
    
    
    def _read_version_record(self, metadata, binary_data):
        if self.cr.describes_transaction_data():
            assert '\xb5' == binary_data[0], repr(binary_data[0])
        else:
            assert '\xb6' == binary_data[0], repr(binary_data[0])
        assert '1' == binary_data[1]
        assert ',' == binary_data[2]
        used_general_ledger_account_no_length = int(binary_data[3])
        assert used_general_ledger_account_no_length >= 4
        assert used_general_ledger_account_no_length <= 8
        metadata['used_general_ledger_account_no_length'] = \
            used_general_ledger_account_no_length
        assert ',' == binary_data[4]
        stored_general_ledger_account_no_length = int(binary_data[5])
        assert stored_general_ledger_account_no_length >= 4
        assert stored_general_ledger_account_no_length <= 8
        metadata['stored_general_ledger_account_no_length'] = \
            stored_general_ledger_account_no_length
        
        # DATEV SELF says in 5.3.2 (p. 152) that the the used account number 
        # length must not be smaller than the stored account number length but
        # DATEV Rechnungswesen does export those files. SELF Prüfprogramm warns
        # that the account numbers will be cut from right so this algorithm is
        # used here, too.
        if used_general_ledger_account_no_length > stored_general_ledger_account_no_length:
            msg_template = "Used general ledger account number in data file " + \
                           "is greater than the stored general ledger " + \
                           "account number (%d vs. %d). Account numbers " + \
                           "will be cut starting from right."
            msg = msg_template % (used_general_ledger_account_no_length, stored_general_ledger_account_no_length)
            warnings.warn(msg, UserWarning, stacklevel=0)
        assert_match(',', binary_data[6])
        
        # DATEV SELF specification says that the product abbreviation is 4 bytes
        # long so the version info for transaction data is 13 bytes in total
        # (5.3.2, p. 152).
        # Unfortunately, DATEV Rechnungswesen may produce files with additional
        # spaces after their 'REWE' identification... 
        # Furthermore 'Kanzlei Rechnungswesen' uses 6 Bytes for their product
        # abbreviation (KAREWE).
        product_abbreviation, end_index = parse_string(binary_data, 7)
        if len(product_abbreviation) > 4:
            msg_template = 'Product abbreviation is longer than 4 bytes: %s'
            warnings.warn(msg_template % repr(product_abbreviation), UserWarning)
        product_abbreviation = product_abbreviation.strip()
        assert_true(re.match('^[\w0-9\-]{4,}$', product_abbreviation) != None, 
                    product_abbreviation)
        self.config['product_abbreviation'] = product_abbreviation
        
        assert_match('\x1c', binary_data[end_index], binary_data)
        assert_match('y', binary_data[end_index + 1])
        return end_index + 1
    
    
    def may_add_transactions_for(self, date_for_new_line):
        '''Returns True if transactions for this date may be added to this data 
        file, otherwise False. Transactions in one data file must all belong to 
        the same financial year. Currently it is assumed that the financial
        year is the same as the calendar year.
        Raises a ValueError if this file does not contain transaction data.'''
        assert_true(self.contains_transaction_data())
        same_financial_year = True
        if len(self.lines) > 0:
            year_for_new_line = date_for_new_line.year
            same_calendar_year = (self.lines[0].date.year == year_for_new_line)
            same_financial_year = same_calendar_year
        return same_financial_year
    
    def more_posting_lines(self, binary_data, end_index):
        if (end_index < len(binary_data)) and \
            (binary_data[end_index] not in ['x', 'w']):
            return True
        return False
    
    
    def more_custom_info_records(self, binary_data, start_index):
        """Return True if there are custom info records available in 
        binary_data at the offset start_index."""
        if start_index < len(binary_data) and binary_data[start_index] == '\xb7':
            return True
        return False
    
    
    def _parse_custom_info_records(self, binary_data, start_index, line):
        end_index = start_index
        while self.more_custom_info_records(binary_data, end_index):
            record, end_index = \
                CustomInfoRecord.from_binary(binary_data, end_index)
            line.custom_info_records.append(record)
            end_index += 1
        # In the last round of the loop we increment the counter although the 
        # loop condition fails afterwards so we need to decrement the end_index.
        # This holds also true if we did not parse any data, because then we 
        # need to fake the end_index so that the character at start_index is 
        # passed to the next function
        end_index -= 1
        return end_index
    
    
    def _check_client_total(self, binary_data, start_index):
        nr_start_index = start_index
        nr_max_end_index = start_index+1+14-1
        client_total, end_index = parse_number(binary_data, nr_start_index, nr_max_end_index)
        if binary_data[start_index] == 'w':
            client_total *= -1
        end_index += 1
        assert 'y' == binary_data[end_index], repr(binary_data[end_index])
        return end_index + 1
    
    
    def _parse_transactions(self, binary_data, start_index, metadata):
        end_index = start_index - 1
        while True:
            # There can be multiple subtotals between the lines so we must 
            # break if we really reached 'client total'
            while self.more_posting_lines(binary_data, start_index):
                line, end_index = PostingLine.from_binary(binary_data, start_index, metadata)
                self.lines.append(line)
                end_index = self._parse_custom_info_records(binary_data, end_index+1, line)
                start_index = end_index + 1
            end_index = self._check_client_total(binary_data, end_index+2)
            if binary_data[end_index] != 'z':
                start_index = end_index
            else:
                break
        return end_index
    
    
    def more_master_data_lines(self, binary_data, start_index):
        if start_index < len(binary_data) and binary_data[start_index] == 't':
            return True
        return False
    
    
    def _parse_master_data(self, binary_data, start_index):
        while self.more_master_data_lines(binary_data, start_index):
            line, end_index = DataLine.from_binary(binary_data, start_index)
            self.lines.append(line)
            start_index = end_index + 1
        assert 'z' == binary_data[start_index]
        return start_index
    
    
    def from_binary(self, binary_control_record, data_fp):
        '''Takes a binary control record and a file-like object which contains
        the data and parses them.'''
        self.open_for_additions = False 
        cr = ControlRecord()
        cr.from_binary(binary_control_record)
        self.cr = cr
        binary_data = data_fp.read()
        metadata = self.get_metadata()
        number_data_blocks = metadata['number_data_blocks']
        assert_true(number_data_blocks > 0, number_data_blocks)
        assert_match(256 * number_data_blocks, len(binary_data))
        binary_data = self._remove_fill_bytes(binary_data, number_data_blocks)
        end_index = self._check_feed_line(metadata, binary_data[:80])
        relative_end_index = self._read_version_record(metadata, binary_data[end_index+1:])
        end_index += relative_end_index + 1
        start_index = end_index + 1
        if self.contains_transaction_data():
            end_index = self._parse_transactions(binary_data, start_index, metadata)
        else:
            end_index = self._parse_master_data(binary_data, start_index)
        err_msg = ('%d + 1 != %d' % (end_index, len(binary_data)))
        assert end_index + 1 == len(binary_data), err_msg
    
    
    def get_metadata(self):
        assert self.cr != None
        return self.cr.parsed_data()
    
    
    def get_posting_lines(self):
        assert_true(self.contains_transaction_data())
        assert_true(not self.open_for_additions)
        return self.lines
    
    
    def get_master_data_lines(self):
        assert not self.contains_transaction_data()
        assert not self.open_for_additions
        return self.lines
    
    
    def to_binary(self):
        if self.version_identifier != None:
            if self.contains_transaction_data():
                feedline = self._get_complete_feed_line()
                vid = self._get_versioninfo_for_transaction_data(self.version_identifier)
            else:
                feedline = self._get_short_feed_line()
                vid = self._get_versioninfo_for_masterdata(self.version_identifier)
            self.binary_info = feedline + vid
        
        self.finish()
        self.number_of_blocks = self._get_number_of_blocks()
        return self.binary_info


