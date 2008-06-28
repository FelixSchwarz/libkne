# -*- coding: UTF-8 -*-

from util import parse_short_date, _short_date

__all__ = ["ControlRecord"]

class ControlRecord(object):
    "Control record after data carrier header in the control file"
    def __init__(self):
        self.file_no = 1
        self.application_number = None
        self.name_abbreviation = None
        self.advisor_number = None
        self.client_number = None
        self.accounting_number = None
        self.accounting_year = None
        self.date_start = None
        self.date_end = None
        self.password = None
        self.prima_nota_page = None
        self.data_fp = None
        
        self.number_of_blocks = None
        self.meta = None
    
    
    def from_binary(self, binary_data):
        assert self.meta == None
        assert len(binary_data) == 128
        assert binary_data[0] in ['V', '*']
        meta = {}
        meta['do_process'] = (binary_data[0] == 'V')
        meta['file_no'] = int(binary_data[1:6])
        meta['application_number'] = int(binary_data[6:8]) # TODO -> 11?
        meta['name_abbreviation'] = binary_data[8:10]
        meta['advisor_number'] = int(binary_data[10:17])
        meta['client_number'] = int(binary_data[17:22])
        meta['accounting_number'] = int(binary_data[22:26])
        meta['accounting_year'] = int(binary_data[26:28])
        assert '0' * 4 == binary_data[28:32]
        meta['date_start'] = parse_short_date(binary_data[32:38])
        meta['date_end'] = parse_short_date(binary_data[38:44])
        meta['prima_nota_page'] = int(binary_data[44:47])
        meta['password'] = binary_data[47:51]
        meta['number_data_blocks'] = int(binary_data[51:56])
        meta['last_prima_nota_page'] = int(binary_data[56:59])
        assert binary_data[59] == ' '
        assert binary_data[60] == '1'
        meta['version_info'] = binary_data[61:71]
        # specification says "linksbündig, mit 4 Leerzeichen aufgefüllt."
        # is this really always 4 spaces or is this just the filling if you 
        # use the "default"(?) "1,4,4,SELF"?
        assert binary_data[71:75] == '    '
        assert ' ' * 53 == binary_data[75:128]
        
        self.meta = meta
        return meta
    
    
    def parsed_data(self):
        assert self.meta != None
        return self.meta
    
    
    def to_binary(self, version_identifier):
        "Return the binary KNE format for the specified data."
        bin_line = 'V' + ("%05d" % self.file_no)
        bin_line += self.application_number
        bin_line += self.name_abbreviation
        bin_line += self.advisor_number
        bin_line += self.client_number
        bin_line += self.accounting_number + str(self.accounting_year)[2:]
        bin_line += '0000' + _short_date(self.date_start)
        bin_line += _short_date(self.date_end)
        bin_line += self.prima_nota_page
        bin_line += self.password
        bin_line += "%05d" % self.number_of_blocks
        bin_line += self.prima_nota_page
        bin_line += ' ' + '1'
        bin_line += version_identifier + '    '
        bin_line += ' ' * 53
        assert len(bin_line) == 128
        return bin_line

