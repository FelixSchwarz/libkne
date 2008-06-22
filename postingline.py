# -*- coding: UTF-8 -*-

from decimal import Decimal
import datetime
import re

from util import get_number_of_decimal_places, parse_number

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
    
    
    def _parse_transaction_volume(self, data):
        assert data[0] in ['+', '-'], repr(data[0])
        volume, end_index = parse_number(data, 1, 10)
        complete_volume = int(data[0] + str(volume))
        volume = Decimal(complete_volume) / Decimal(100)
        self.transaction_volume = volume
        return end_index
    
    
    def _parse_offsetting_account(self, data, start_index):
        assert 'a' == data[start_index]
        start = start_index+1
        # TODO: Laenge der aufgezeichneten Nummern überprüfen!
        account, end_index = parse_number(data, start, start+9)
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
        account, end_index = parse_number(data, start, start+9)
        self.account_number  = account
        return end_index
    
    
    def _parse_posting_text(self, data, start_index):
        index = start_index
        if data[start_index] == '\x1e':
            index = start_index + 1
            while data[index] != '\x1c' and index < start_index + 30 - 1:
                index += 1
            assert data[index] == '\x1c', repr(data[index])
            text = data[start_index+1:index]
            self.posting_text = text.decode('datev_ascii')
        return index
    
    
    def _parse_currency_code(self, data, start_index):
        assert '\xb3' == data[start_index]
        index = start_index + 1
        while data[index] != '\x1c' and index <= start_index + 3:
            index += 1
        assert data[index] == '\x1c'
        code = data[start_index+1:index].upper()
        self.currency_code_transaction_volume = code
        return index
    
    
    @classmethod
    def from_binary(cls, binary_data, start_index, metadata):
        data = binary_data[start_index:]
        line = cls()
        #print repr(data)
        end_index = line._parse_transaction_volume(data)
        end_index = line._parse_offsetting_account(data, end_index+1)
        end_index = line._parse_record_field(data, end_index+1, '\xbd', 'record_field1')
        end_index = line._parse_record_field(data, end_index+1, '\xbe', 'record_field2')
        end_index = line._parse_transaction_date(data, end_index+1, metadata)
        end_index = line._parse_account(data, end_index+1)
        end_index = line._parse_posting_text(data, end_index+1)
        end_index = line._parse_currency_code(data, end_index+1)
        #print repr(data[end_index-2:])
        assert 'y' == data[end_index + 1]
        end_index += 1
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

