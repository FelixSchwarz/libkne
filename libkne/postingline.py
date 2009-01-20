# -*- coding: UTF-8 -*-

from decimal import Decimal
import datetime
import re

from libkne.util import assert_true, get_number_of_decimal_places, \
    parse_number, parse_number_field, parse_optional_string_field, parse_string

__all__ = ['PostingLine']

class PostingLine(object):
    def __init__(self, file_metadata):
        self.file_metadata = file_metadata
        
        self.transaction_volume = None
        self.amendment_key = None
        self.tax_key = None         # TODO: write to binary
        self.offsetting_account = None
        self.record_field1 = None
        self.record_field2 = None
        self.date = None
        self.account_number = None
        self.cost_center1 = None
        self.cost_center2 = None
        self.cash_discount = None           # TODO: Write to binary
        self.posting_text = None
        self.eu_id = None
        self.eu_state = None
        self.vat_id = None
        self.eu_taxrate = None
        self.currency_code_transaction_volume = None
        self.base_currency_amount = None    # TODO: Write to binary!
        self.base_currency = None           # TODO: Write to binary!
        self.exchange_rate = None           # TODO: Write to binary!
        
        char_re = '([^0-9a-zA-Z\$%&*\+-/])'
        self.record_field_valid_characters = re.compile(char_re)
    
    
    def _parse_transaction_volume(self, data):
        assert_true(data[0] in ['+', '-'], data[0])
        volume, end_index = parse_number(data, 1, 10)
        complete_volume = int(data[0] + str(volume))
        volume = Decimal(complete_volume) / Decimal(100)
        self.transaction_volume = volume
        return end_index
    
    
    def _parse_posting_key(self, data, start_index):
        if data[start_index] == 'l':
            start = start_index + 1
            amendment_key, end_index = parse_number(data, start, start+1)
            amendment_key = str(amendment_key)
            assert_true(len(amendment_key) in [1, 2])
            if len(amendment_key) == 1:
                amendment_key = "0" + amendment_key
            self.amendment_key = int(amendment_key[0]) or None
            self.tax_key = int(amendment_key[1])
            return end_index
        else:
            return start_index - 1
    
    
    def _parse_record_field(self, data, start_index, first_character, attr_name):
        if data[start_index] == first_character:
            start = start_index+1
            match = re.match('^([0-9a-zA-Z$%&\*\+\-/]{1,12})\x1c', data[start:])
            if match != None:
                record_field = match.group(1)
                setattr(self, attr_name, record_field)
                end_index = start + len(record_field) - 1 + 1
                return end_index
            assert False, 'Could not parse record field: ' + repr(data[start:(start+12)])
        return start_index - 1
    
    
    def _parse_transaction_date(self, data, start_index, metadata):
        assert 'd' == data[start_index], repr(data[start_index])
        date_number, end_index = parse_number(data, start_index+1, start_index+5)
        
        day = int(str(date_number)[:-2])
        month = int(str(date_number)[-2:])
        date_start = metadata['date_start']
        date_end = metadata['date_end']
        if month >= date_start.month:
            year = date_start.year
        else:
            assert month <= date_end.year
            year = date_end.year
        self.date = datetime.date(year, month, day)
        return end_index
    
    
    def _parse_account(self, data, start_index):
        assert 'e' == data[start_index]
        start = start_index+1
        # TODO: Laenge der aufgezeichneten Nummern überprüfen!
        
        #stored_general_ledger_account_no_length
        account, end_index = parse_number(data, start, start+9)
        self.account_number  = account
        return end_index
    
    
    def _parse_cash_discount(self, data, start_index):
        if data[start_index] == 'h':
            start = start_index + 1
            cash_discount, end_index = parse_number(data, start, start+10)
            self.cash_discount = Decimal(cash_discount) / Decimal(100)
            return end_index
        return start_index - 1
    
    
    def _parse_posting_text(self, data, start_index):
        value, end_index = parse_optional_string_field(data, '\x1e', start_index, 30)
        if value != None:
            self.posting_text = value.decode('datev_ascii')
        return end_index
    
    
    def _parse_cost_center(self, data, start_index):
        if data[start_index] == '\xbb':
            end_index = start_index + 1
            max_end_index = end_index + 8 - 1
            while data[end_index] != '\x1c' and end_index <= max_end_index:
                end_index += 1
            assert data[end_index] == '\x1c', repr(data[end_index])
            text = data[start_index+1:end_index]
            self.cost_center1 = text
            return end_index
        return start_index - 1
    
    
    def _parse_currency_code(self, data, start_index):
        assert '\xb3' == data[start_index], repr(data[start_index])
        index = start_index + 1
        while data[index] != '\x1c' and index <= start_index + 3:
            index += 1
        assert data[index] == '\x1c'
        code = data[start_index+1:index].upper()
        self.currency_code_transaction_volume = code
        return index
    
    
    def _parse_base_currency_amount(self, data, start_index):
        if data[start_index] == 'm':
            start = start_index + 1
            base_currency_amount, end_index = parse_number(data, start, start+12)
            self.base_currency_amount = Decimal(base_currency_amount) / Decimal(100)
            return end_index
        return start_index - 1
    
    
    def _parse_base_currency(self, data, start_index):
        if data[start_index] == '\xb4':
            start = start_index + 1
            base_currency, end_index = parse_string(data, start, start+3)
            self.base_currency = base_currency
            return end_index
        return start_index - 1
    
    
    def _parse_exchange_rate(self, data, start_index):
        if data[start_index] == 'n':
            start = start_index + 1
            exchange_rate, end_index = parse_number(data, start, start+11)
            self.exchange_rate = Decimal(exchange_rate) / Decimal(1000000)
            return end_index
        return start_index - 1
    
    
    @classmethod
    def from_binary(cls, binary_data, start_index, metadata):
        data = binary_data[start_index:]
        line = cls(file_metadata=metadata)
        end_index = line._parse_transaction_volume(data)
        end_index = line._parse_posting_key(data, end_index+1)
        
        account_no_length = line.file_metadata.get('stored_general_ledger_account_no_length')
        # sub-ledger account numbers contain 1 digit more than general ledger
        # account numbers
        result = \
            parse_number_field(data, 'a', end_index+1, 9, restrict_number_length=account_no_length+1)
        (line.offsetting_account, end_index) = result
        
        end_index = line._parse_record_field(data, end_index+1, '\xbd', 'record_field1')
        end_index = line._parse_record_field(data, end_index+1, '\xbe', 'record_field2')
        end_index = line._parse_transaction_date(data, end_index+1, metadata)
        end_index = line._parse_account(data, end_index+1)
        end_index = line._parse_cost_center(data, end_index+1)
        end_index = line._parse_cash_discount(data, end_index+1)
        end_index = line._parse_posting_text(data, end_index+1)
        end_index = line._parse_currency_code(data, end_index+1)
        end_index = line._parse_base_currency_amount(data, end_index+1)
        end_index = line._parse_base_currency(data, end_index+1)
        end_index = line._parse_exchange_rate(data, end_index+1)
        assert 'y' == data[end_index + 1], repr(data[end_index + 1:])
        end_index += 1
        return (line, start_index + end_index)
    
    
    def _assert_only_valid_characters_for_record_field(self, value):
        match = self.record_field_valid_characters.search(value)
        if match != None:
            invalid_char = match.group(1)
            msg = 'Invalid character in record field: ' + repr(invalid_char)
            raise ValueError(msg)
    
    
    def _encode_posting_text(self, value):
        if not isinstance(value, unicode):
            # filtering, only allow specified characters
            value = value.decode('datev_ascii')
        value = value.encode('datev_ascii')
        return value
    
    
    def _transaction_volume_to_binary(self):
        value = self.transaction_volume
        if isinstance(value, (int, long)):
            bin_volume = '%+d00' % value
        elif isinstance(value, Decimal):
            dec_places = get_number_of_decimal_places(str(value))
            if dec_places > 2:
                msg = 'Loosing precision when cutting "%s" to 2 decimal places!'
                raise ValueError(msg % str(value))
            bin_volume = '%+d' % int(100 * value)
        else:
            msg = 'unknown type for transaction volume: ' + str(value.__class__)
            raise ValueError(msg)
        if value == 0:
            raise ValueError('Transaction volume must not be zero!')
        return bin_volume
    
    
    def _date_to_binary(self):
        assert self.date != None
        bin_date = '%d%02d' % (self.date.day, self.date.month)
        return bin_date
    
    
    def to_binary(self):
        'Return the binary KNE format for the specified data.'
        assert self.cost_center1 == None # not yet implemented
        assert self.cost_center2 == None # not yet implemented
        bin_line = self._transaction_volume_to_binary()
        if self.amendment_key != None:
            amendment_key = str(int(self.amendment_key))
            assert len(amendment_key) == 1
            bin_line += 'l' + amendment_key + '0'
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

