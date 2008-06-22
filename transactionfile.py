# -*- coding: UTF-8 -*-

import math

from controlrecord import ControlRecord
from postingline import PostingLine
from util import parse_short_date, _short_date, parse_number

class TransactionFile(object):
    
    def __init__(self, config, version_identifier=None):
        self.config = config
        self.binary_info = None
        if version_identifier != None:
            self.binary_info = self._get_complete_feed_line()
            vid = self._get_versioninfo_for_transaction_data(version_identifier)
            self.binary_info += vid
        self.lines = []
        self.cr = None
        
        self.open_for_additions = (self.binary_info != None)
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
        
        bin_total += "%014d" % int_total 
        bin_total += 'y' + 'z'
        return bin_total
    
    
    def _get_complete_feed_line(self):
        start_feed_line = '\x1d'
        new_feed = '\x18'
        
        bin_line = start_feed_line + new_feed
        bin_line += self.config["version_complete_feed_line"]
        bin_line += "%03d" % self.config["data_carrier_number"]
        bin_line += self.config["application_number"]
        bin_line += self.config["name_abbreviation"]
        bin_line += self.config["advisor_number"]
        bin_line += self.config["client_number"]
        bin_line += self.config["accounting_number"] + str(self.config["accounting_year"])[2:]
        bin_line += _short_date(self.config["date_start"])
        bin_line += _short_date(self.config["date_end"])
        bin_line += self.config["prima_nota_page"]
        bin_line += self.config["password"]
        bin_line += self.config["application_info"]
        bin_line += self.config["input_info"]
        bin_line += 'y'
        assert len(bin_line) == 80
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
    
    
    def append_posting_line(self, line):
        """Append a new posting line to this transaction file (only if 
        to_binary() was not called before on this file!). Return True if the 
        line was appended successfully else False. If False, no 
        more lines can be appended to this file."""
        assert self.open_for_additions
        self.lines.append(line)
        return True
    
    
    def build_control_record(self):
        cr = ControlRecord()
        cr.application_number = self.config["application_number"]
        cr.name_abbreviation = self.config["name_abbreviation"]
        cr.advisor_number = self.config["advisor_number"]
        cr.client_number = self.config["client_number"]
        cr.accounting_number = self.config["accounting_number"]
        cr.accounting_year = self.config["accounting_year"]
        cr.date_start = self.config["date_start"]
        cr.date_end = self.config["date_end"]
        cr.prima_nota_page = self.config["prima_nota_page"]
        cr.password = self.config["password"]
        
        cr.number_of_blocks = self.number_of_blocks
        self.cr = cr
        return cr
    
    
    def contains_transaction_data(self):
        return self.transaction_data
    
    
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
                binary_line = line.to_binary()
                self.binary_info += self._insert_fill_bytes(binary_line)
            self.binary_info += self._client_total()
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
    
    
    def _check_complete_feed_line(self, metadata, binary_data):
        assert len(binary_data) == 80
        assert binary_data[0] == '\x1d', repr(binary_data[0])
        assert binary_data[1] == '\x18'
        assert binary_data[2] == '1'
        assert metadata['file_no'] == int(binary_data[3:6])
        assert 11 == int(binary_data[6:8]) # FIBU/OPOS transaction data
        assert metadata['name_abbreviation'] == binary_data[8:10]
        assert metadata['advisor_number'] == int(binary_data[10:17])
        assert metadata['client_number'] == int(binary_data[17:22])
        assert metadata['accounting_number'] == int(binary_data[22:26])
        assert metadata['accounting_year'] == int(binary_data[26:28])
        date_start = parse_short_date(binary_data[28:34])
        assert metadata['date_start'] == date_start
        date_end = parse_short_date(binary_data[34:40])
        assert metadata['date_end'] == date_end
        assert metadata['prima_nota_page'] == int(binary_data[40:43])
        assert metadata['password'] == binary_data[43:47]
        # Specification says "Anwendungsinfo"/"Konstante" - maybe this is a 
        # field which can be used arbitrarily?
        assert ' ' * 16 == binary_data[47:63]
        # Specification says "Input-Info"/"Konstante" - maybe this is a 
        # field which can be used arbitrarily?
        assert ' ' * 16 == binary_data[63:79]
        assert 'y' == binary_data[79]
    
    
    def _read_version_record(self, metadata, binary_data):
        assert len(binary_data) == 13
        if '\xb5' == binary_data[0]:
            self.transaction_data = True
        else:
            assert False
        assert '1' == binary_data[1]
        assert ',' == binary_data[2]
        used_general_ledger_account_no_length = int(binary_data[3])
        assert used_general_ledger_account_no_length >= 4
        assert used_general_ledger_account_no_length <= 8
        metadata["used_general_ledger_account_no_length"] = \
            used_general_ledger_account_no_length
        assert ',' == binary_data[4]
        stored_general_ledger_account_no_length = int(binary_data[5])
        assert stored_general_ledger_account_no_length >= 4
        assert stored_general_ledger_account_no_length <= 8
        metadata["stored_general_ledger_account_no_length"] = \
            stored_general_ledger_account_no_length
        assert stored_general_ledger_account_no_length >= used_general_ledger_account_no_length
        assert ',' == binary_data[6]
        # Specification says: "Produktkürzel"/"Konstante"
        assert 'SELF' == binary_data[7:11]
        assert '\x1c' == binary_data[11]
        assert 'y' == binary_data[12]
    
    
    def more_posting_lines(self, binary_data, end_index):
        return (binary_data[end_index] not in ['x', 'w'])
    
    
    def _check_client_total(self, binary_data, start_index):
        nr_start_index = start_index + 1
        nr_max_end_index = start_index+1+14-1
        client_total, end_index = parse_number(binary_data, nr_start_index, nr_max_end_index)
        if binary_data[start_index] == 'w':
            client_total *= -1
        assert 'y' == binary_data[end_index+1], repr(binary_data[end_index+1])
        assert 'z' == binary_data[end_index+2], repr(binary_data[end_index+2])
        return end_index + 2
    
    
    def from_binary(self, binary_control_record, data_fp):
        """Takes a binary control record and a file-like object which contains
        the data and parses them."""
        cr = ControlRecord()
        cr.from_binary(binary_control_record)
        self.cr = cr
        binary_data = data_fp.read()
        metadata = self.get_metadata()
        number_data_blocks = metadata["number_data_blocks"]
        assert number_data_blocks > 0
        assert 256 * number_data_blocks == len(binary_data)
        # remove fill bytes
        binary_data = self._remove_fill_bytes(binary_data, number_data_blocks)
        self._check_complete_feed_line(metadata, binary_data[:80])
        self._read_version_record(metadata, binary_data[80:93])
        end_index = 93 - 1
        start_index = end_index + 1
        while (start_index < len(binary_data)) and \
            (self.more_posting_lines(binary_data, start_index)):
            line, end_index = PostingLine.from_binary(binary_data, start_index, metadata)
            self.lines.append(line)
            start_index = end_index + 1
        end_index = self._check_client_total(binary_data, end_index+1)
        index = end_index + 1
        while index + 1 < len(binary_data):
            assert '\x00' == binary_data[index]
            index += 1
    
    
    def get_metadata(self):
        assert self.cr != None
        return self.cr.parsed_data()
    
    
    def get_posting_lines(self):
        assert not self.open_for_additions
        return self.lines
    
    
    def to_binary(self):
        self.finish()
        self.number_of_blocks = self._get_number_of_blocks()
        return self.binary_info

