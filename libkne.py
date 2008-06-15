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



class TransactionFile(object):
    
    def __init__(self, config, version_identifier):
        self.config = config
        self.binary_info = self._get_complete_feed_line()
        vid = self._get_versioninfo_for_transaction_data(version_identifier)
        self.binary_info += vid
        self.lines = []
        
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
        return cr
    
    
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
    
    
    def to_binary(self):
        self.finish()
        self.number_of_blocks = self._get_number_of_blocks()
        
        return self.binary_info



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
        for metainfo, data_fp in zip(meta_info_list, data_fps):
            data_file = self._parse_data_file(metainfo, data_fp)
    
    
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
            meta_info_list.append(meta_info_list)
        return meta_info_list
    
    
    def _parse_data_file(self, metainfo, data_fp):
        pass
    
    
    def get_config(self):
        return self.config



class KneFileReader(KneReader):
    "Reads the data from the file system and passes them to the KneReader"
    
    def __init__(self, header_filename=None, data_filenames=None):
        assert header_filename != None
        header_fp = StringIO(file(header_filename, "rb").read())
        data_fps = []
        if data_filenames != None:
            for filename in data_filenames:
                fake_fp = StringIO(file(header_filename, "rb").read())
                data_fps.append(fake_fp)
        super(KneFileReader, self).__init__(header_fp=header_fp, 
                                            data_fps=data_fps)

"""
Translation terms used within this library

Deutsch/German                Englisch/English
-----------------------------------------------------------------
Abrechnungsnummer             accounting number
Anwendungsnummer              application number
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
Verwaltungssatz               control record
Vollvorlauf                   complete feed line
Währungskennzeichen           Währungskennzeichen
Währungskurs                  exchange rate
Wirtschaftsjahr               financial year
"""

