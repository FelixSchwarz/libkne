# -*- coding: UTF-8 -*-

import datetime
from decimal import Decimal
import math
import re
from StringIO import StringIO

import datev_encoding
datev_encoding.register()


def _short_date(date):
    format = "%02d%02d%02d"
    short_year = int(str(date.year)[2:])
    return format % (date.day, date.month, short_year)

# ------------------------------------------------------------------------------
sciformat_regex = re.compile("^(-?\d+(?:\.\d+)?)(?:E(\+\d+))?$")
def append_zeroes(old_number, dot_index, new_dot_index):
    numbers_after_dot = len(old_number) - dot_index
    new_number = old_number[:dot_index] + old_number[(dot_index+1):]
    if float(old_number) > 0:
        additional_zeroes = new_dot_index - numbers_after_dot
    else:
        additional_zeroes = new_dot_index - numbers_after_dot - 1
    return new_number + ("0" * additional_zeroes)


def format_to_normal(dec):
    decstr = str(dec.normalize())
    match = sciformat_regex.match(decstr)
    assert match != None, decstr
    number, exponent = match.groups()
    if exponent == None:
        return number
    
    exponent = int(exponent)
    assert exponent > 0
    if "." not in number:
        return number + ("0" * exponent)
    dot_index = number.index(".")
    new_dot_index = dot_index + exponent
    assert new_dot_index >= len(number)
    return append_zeroes(number, dot_index, new_dot_index)


def get_number_of_decimal_places(number_string):
    if "." in number_string:
        dot_index = number_string.index(".")
        return len(number_string) - dot_index - 1
    return 0
# ------------------------------------------------------------------------------


def parse_short_date(binary_data):
    '''Parses a short date with the format "DDMMJJ" into a real datetime.date.
    Years lower than 60 are interpreted as 19xx, all other years as 20xx.'''
    assert len(binary_data) == 6, len(binary_data)
    day = int(binary_data[:2])
    month = int(binary_data[2:4])
    year = int(binary_data[4:])
    if year < 60:
        year += 2000
    else:
        year += 1900
    return datetime.date(year, month, day)



class PostingLine(object):
    def __init__(self):
        self.transaction_volume = None
        self.posting_key = None
        self.offsetting_account = None
        self.record_field1 = None
        self.record_field2 = None
        self.date = None
        self.account_number = None
        self.cash_discount = None
        self.posting_text = None
        self.eu_id = None
        self.eu_state = None
        self.vat_id = None
        self.eu_taxrate = None
        self.currency_code_transaction_volume = None
        self.base_currency_amount = None
        self.exchange_rate = None
        
        char_re = "([^0-9a-zA-Z\$%&*\+-/])"
        self.record_field_valid_characters = re.compile(char_re)
    
    
    def _parse_number(self, data, start_index, max_end_index):
        string_number = ''
        for i in range(start_index, max_end_index):
            if data[i] not in map(str, range(10)):
                break
            string_number += data[i]
        end_index = start_index + len(string_number) - 1
        return (int(string_number), end_index)
    
    
    def _parse_transaction_volume(self, data):
        assert data[0] in ['+', '-'], repr(data[0])
        volume, end_index = self._parse_number(data, 1, 10)
        complete_volume = int(data[0] + str(volume))
        volume = Decimal(complete_volume) / Decimal(100)
        self.transaction_volume = volume
        return end_index
    
    
    def _parse_offsetting_account(self, data, start_index):
        end_index = start_index
        if data[start_index] == 'a':
            start = start_index+1
            # TODO: Laenge der aufgezeichneten Nummern überprüfen!
            account, end_index = self._parse_number(data, start, start+9)
            self.offsetting_account = account
        return end_index
    
    
    def _parse_record_field(self, data, start_index, first_character, attr_name):
        end_index = start_index
        if data[start_index] == first_character:
            start = start_index+1
            match = re.match('^([0-9a-zA-Z$%&\*\+\-/]{1,12})\x1c', data[start:])
            if match != None:
                record_field = match.group(1)
                setattr(self, attr_name, record_field)
                end_index = start + len(record_field) - 1 + 1
        return end_index
    
    
    def _parse_transaction_date(self, data, start_index, metadata):
        assert 'd' == data[start_index]
        day = int(data[start_index+1:start_index+3])
        month = int(data[start_index+3:start_index+5])
        
        date_start = metadata['date_start']
        date_end = metadata['date_end']
        if month >= date_start.month:
            year = date_start.year
        else:
            assert month <= date_end.year
            year = date_end.year
        self.date = datetime.date(year, month, day)
        end_index = start_index + 4
        return end_index
    
    
    def _parse_account(self, data, start_index):
        assert 'e' == data[start_index]
        start = start_index+1
        # TODO: Laenge der aufgezeichneten Nummern überprüfen!
        account, end_index = self._parse_number(data, start, start+9)
        self.account_number  = account
        return end_index
    
    
    def _parse_posting_text(self, data, start_index):
        assert '\x1e' == data[start_index]
        index = start_index + 1
        while data[index] != '\x1c' and index < start_index + 30 - 1:
            index += 1
        assert data[index] == '\x1c'
        text = data[start_index+1:index]
        self.posting_text = text.decode('datev_ascii')
        return index
    
    
    @classmethod
    def from_binary(cls, binary_data, start_index, metadata):
        data = binary_data[start_index:]
        line = cls()
        end_index = line._parse_transaction_volume(data)
        end_index = line._parse_offsetting_account(data, end_index+1)
        end_index = line._parse_record_field(data, end_index+1, '\xbd', 'record_field1')
        end_index = line._parse_record_field(data, end_index+1, '\xbe', 'record_field2')
        end_index = line._parse_transaction_date(data, end_index+1, metadata)
        end_index = line._parse_account(data, end_index+1)
        end_index = line._parse_posting_text(data, end_index+1)
        return (line, start_index + end_index)
    
    
    def _assert_only_valid_characters_for_record_field(self, value):
        match = self.record_field_valid_characters.search(value)
        if match != None:
            invalid_char = match.group(1)
            msg = "Invalid character in record field: " + repr(invalid_char)
            raise ValueError(msg)
    
    
    def _encode_posting_text(self, value):
        if not isinstance(value, unicode):
            # filtering, only allow specified characters
            value = value.decode("datev_ascii")
        value = value.encode("datev_ascii")
        return value
    
    
    def _transaction_volume_to_binary(self):
        value = self.transaction_volume
        if isinstance(value, (int, long)):
            bin_volume = '%+d00' % value
        elif isinstance(value, Decimal):
            dec_places = get_number_of_decimal_places(str(value))
            if dec_places > 2:
                msg = "Loosing precision when cutting '%s' to 2 decimal places!"
                raise ValueError(msg % str(value))
            bin_volume = '%+d' % (100 * value)
        else:
            msg = "unknown type for transaction volume: " + str(value.__class__)
            raise ValueError(msg)
        return bin_volume
    
    
    def _date_to_binary(self):
        assert self.date != None
        bin_date = '%d%02d' % (self.date.day, self.date.month)
        return bin_date
    
    
    def to_binary(self):
        "Return the binary KNE format for the specified data."
        bin_line = self._transaction_volume_to_binary()
        assert self.offsetting_account != None
        bin_line += 'a' + str(self.offsetting_account)
        assert len(self.record_field1) <= 12
        self._assert_only_valid_characters_for_record_field(self.record_field1)
        bin_line += '\xbd' + self.record_field1 + '\x1c'
        assert len(self.record_field2) <= 12
        self._assert_only_valid_characters_for_record_field(self.record_field2)
        bin_line += '\xbe' + self.record_field2 + '\x1c'
        bin_line += 'd' + self._date_to_binary()
        bin_line += 'e' + str(self.account_number)
        assert len(self.posting_text) <= 30
        encoded_text = self._encode_posting_text(self.posting_text)
        bin_line += '\x1e' + encoded_text + '\x1c'
        currency_code = self.currency_code_transaction_volume
        assert len(currency_code) <= 3
        assert currency_code.upper() == currency_code
        bin_line += '\xb3' + currency_code + '\x1c'
        bin_line += 'y'
        return bin_line



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
        """Write all transaction files using the data_fp_builder. No 
        transaction data may be appended after calling finish (although 
        finish() itself may be called multiple times.
        Return a list of control records. 
        """
        control_records = []
        for i, tf in enumerate(self.transaction_files):
            data_fp = self.data_fp_builder(i)
            data_fp.write(tf.to_binary())
            control_records.append(tf.build_control_record())
        return control_records



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
    
    
    def _check_complete_feed_line(self, metadata, binary_data):
        assert len(binary_data) == 80
        assert binary_data[0] == '\x1d', repr(binary_data[0])
        assert binary_data[1] == '\x18'
        assert binary_data[2] == '1'
        assert metadata['file_no'] == int(binary_data[3:6])
        print repr(binary_data[6:])
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
        self._check_complete_feed_line(metadata, binary_data[:80])
        self._read_version_record(metadata, binary_data[80:93])
        end_index = 93 - 1
        while (end_index < len(binary_data)):
            start_index = end_index + 1
            line, end_index = PostingLine.from_binary(binary_data, start_index, metadata)
            self.lines.append(line)
            break
    
    
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



product_abbreviation = "lkne"

class KneWriter(object):
    
    def __init__(self, config=None, header_fp=None, data_fp_builder=None):
        """header_fp is a file-like object which will be used to store the KNE
        header. data_fp_builder is a callable that will return a file-like 
        object when called with the number of previously retrieved fp as a an
        argument. These file-like objects will be used to store the data items 
        (transaction data or master data)."""
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
        config.setdefault("data_carrier_number", 0)
        assert int(config["data_carrier_number"]) in range(0,999)
        config.setdefault("gl_account_no_length_data", 8)
        config.setdefault("gl_account_no_length_coredata", 8)
        gl_account_no_length_data = config["gl_account_no_length_data"]
        gl_account_no_length_coredata = config["gl_account_no_length_coredata"]
        assert gl_account_no_length_data in range(4,9)
        assert gl_account_no_length_coredata in range(4,9)
        assert not (gl_account_no_length_data < gl_account_no_length_coredata)
        
        if config.get('advisor_name') != None:
            config['advisor_name'] = "% -9s" % config['advisor_name']
            assert len(config['advisor_name']) == 9
        
        assert int(config["advisor_number"]) > 0
        assert len(str(config["advisor_number"])) in range(1,8)
        config["advisor_number"] = "%07d" % int(config["advisor_number"])
        
        assert int(config["client_number"]) > 0
        assert len(str(config["client_number"])) in range(1,6)
        config["client_number"] = "%05d" % int(config["client_number"])
        
        assert len(config["name_abbreviation"]) == 2
        config["name_abbreviation"] = config["name_abbreviation"].upper()
        
        config.setdefault("accounting_number", 1)
        assert len(str(config["accounting_number"])) in range(1,5)
        config["accounting_number"] = "%04d" % int(config["accounting_number"])
        
        config.setdefault("accounting_year", datetime.date.today().year)
        assert len(str(config["accounting_year"])) == 4
        
        config.setdefault("password", "    ")
        assert len(config["password"]) == 4
        
        assert config["date_start"] != None
        assert config["date_end"] != None
        assert config["date_start"] <= config["date_end"]
        
        config.setdefault("prima_nota_page", 1)
        config["prima_nota_page"] = "%03d" % int(config["prima_nota_page"])
        assert len(config["prima_nota_page"]) == 3
        
        # should not be set from the user as this are more or less constants
        config.setdefault("version_complete_feed_line", '1')
        config.setdefault("application_number", '11') # Fibu/OPOS transaction data
        
        config.setdefault("application_info", " " * 16)
        config["application_info"] ="% -16s" % config["application_info"]
        assert len(config["application_info"]) == 16
        
        config.setdefault("input_info", " " * 16)
        config["input_info"] ="% -16s" % config["input_info"]
        assert len(config["input_info"]) == 16
        
        return config
    
    
    def get_version_identifier(self):
        bin_versionid = '1,'
        bin_versionid += str(self.config["gl_account_no_length_data"])
        bin_versionid += ','
        bin_versionid += str(self.config["gl_account_no_length_coredata"])
        bin_versionid += ','
        assert len(product_abbreviation) == 4
        assert str(product_abbreviation) == product_abbreviation
        bin_versionid += str(product_abbreviation)
        return bin_versionid
    
    
    def _build_data_carrier_header(self, number_of_files):
        bin_line = "%03d" % self.config["data_carrier_number"]
        bin_line += '   '
        bin_line += self.config["advisor_number"]
        bin_line += self.config['advisor_name']
        bin_line += ' '
        bin_line += "%05d" % number_of_files
        bin_line += "%05d" % number_of_files
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
    
    
    def finish(self):
        """Write all data to the given file-like objects and generate the header
        file contents."""
        control_records = self.transaction_manager.finish()
        header_string = self._build_control_header(control_records)
        self.header_fp.write(header_string)



class KneReader(object):
    
    def __init__(self, header_fp=None, data_fps=None):
        """header_fp is a file-like object which contains the header file 
        contents. data_fps is a list of file-like objects which contain the
        real data."""
        self.config, data_meta_information = \
            self._parse_data_carrier_header(header_fp)
        if data_fps == None:
            data_fps = []
        number_data_files = self.config["number_data_files"]
        assert number_data_files == len(data_fps)
        # How can this be different?
        assert self.config["number_last_data_file"] == number_data_files
        assert len(data_fps) == int(len(data_meta_information) / 128)
        meta_info_list = self._split_meta_info_for_data(data_meta_information)
        self.files = []
        for metainfo, data_fp in zip(meta_info_list, data_fps):
            transaction_file = self._parse_data_file(metainfo, data_fp)
            self.files.append(transaction_file)
    
    
    def _parse_data_carrier_header(self, header_fp):
        config = {}
        contents = header_fp.read()
        assert (len(contents) > 0) and ((len(contents) % 128) == 0)
        config["data_carrier_number"] = int(contents[:3])
        assert ("   " == contents[3:6])
        config["advisor_number"] = int(contents[6:13])
        config["advisor_name"] = contents[13:22].strip()
        assert (" " == contents[22])
        config["number_data_files"] = int(contents[23:28])
        config["number_last_data_file"] = int(contents[28:33])
        assert (" "*95 == contents[33:128])
        return config, contents[128:]
    
    
    def _split_meta_info_for_data(self, data_meta_information):
        number_of_blocks = int(len(data_meta_information) / 128)
        meta_info_list = []
        for i in range(number_of_blocks):
            data = data_meta_information[(i * 128):((i + 1) * 128)]
            meta_info_list.append(data)
        return meta_info_list
    
    
    def _parse_data_file(self, binary_control_record, data_fp):
        tf = TransactionFile(self.config)
        tf.from_binary(binary_control_record, data_fp)
        return tf
    
    
    def get_config(self):
        return self.config
    
    
    def get_file(self, index):
        return self.files[index]
    
    
    def get_number_of_files(self):
        return len(self.files)



class KneFileReader(KneReader):
    "Reads the data from the file system and passes them to the KneReader"
    
    def __init__(self, header_filename=None, data_filenames=None):
        assert header_filename != None
        header_fp = StringIO(file(header_filename, "rb").read())
        data_fps = []
        if data_filenames != None:
            for filename in data_filenames:
                fake_fp = StringIO(file(filename, "rb").read())
                data_fps.append(fake_fp)
        super(KneFileReader, self).__init__(header_fp=header_fp, 
                                            data_fps=data_fps)

"""
Translation terms used within this library

Deutsch/German                Englisch/English
-----------------------------------------------------------------
Abrechnungsnummer             accounting number
Anwendungsnummer              application number
Aufgezeichnete Sachkontonummernlänge
                              used general ledger account number length
Basiswährungsbetrag           base currency amount
Belegfeld                     record field
Beraternummer                 advisor number
Bewegungsdaten                transaction data
Buchungsschlüssel             posting key
Buchungstext                  posting text
Buchungszeile                 posting line
Datenträgerkennsatz           data carrier header
Datenträgernummer             data carrier number
Gegenkonto                    offsetting account
Gespeicherte Sachkontonummernlänge
                              stored general ledger account number length
Konto                         account
Mandantennummer               client number
Namenskürzel                  name abbreviation
Primanota                     prima nota
Produktkürzel                 product abbreviation
Sachkonto                     general ledger account
Skonto                        cash discount
Stammdaten                    master data
Umsatz (einer Buchung)        transaction volume
Versionskennung               version identifier
Versionssatz                  version record
Verwaltungssatz               control record
Vollvorlauf                   complete feed line
Währungskennzeichen           currency code
Währungskurs                  exchange rate
Wirtschaftsjahr               financial year
"""

