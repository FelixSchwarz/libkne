# -*- coding: UTF-8 -*-

from util import parse_string_field, parse_optional_number_field, parse_number_field

__all__ = ['DataLine']

class DataLine(object):
    def __init__(self, key=None, text=None, key2=None):
        self.key = key
        self.text = text
        self.aggregation_or_adjustment_key = key2
    
    
    def __eq__(self, other):
        if isinstance(other, DataLine):
            same_key = (self.key == other.key)
            same_text = (self.text == other.text)
            same_key2 = (self.aggregation_or_adjustment_key == other.aggregation_or_adjustment_key)
            return same_key and same_text and same_key2
        return False
    
    
    def __ne__(self, other):
        return not (self == other)
    
    
    def __repr__(self):
        return '%s<%d, "%s", %s>' % (self.__class__.__name__, self.key, repr(self.text), self.aggregation_or_adjustment_key)
    
    
    @classmethod
    def from_binary(cls, binary_data, start_index):
        line = cls()
        key, end_index = parse_number_field(binary_data, 't', start_index, 9)
        line.key = key
        read_digits = end_index - start_index
        if read_digits < 4:
            is_id = True
        else:
            is_account_nr = True
        text, end_index = parse_string_field(binary_data, '\x1e', end_index+1, 40)
        line.text = text.decode("datev_ascii")
        key2, end_index = parse_optional_number_field(binary_data, 'u', 
                                                      end_index+1, 10)
        line.aggregation_or_adjustment_key = key2
        # TODO: Do something with the data here!
        # Basic Algorithm:
        #    if account_nr:
        #        just add an account
        #    else:
        #        aggregate all data between 101
        #        8xx -> Zahlungsbedingungen
        assert 'y' == binary_data[end_index+1], repr(binary_data[end_index+1])
        return (line, end_index+1)
    
    
    def to_binary(self):
        assert len(str(self.key)) <= 9
        text = unicode(self.text).encode('datev_ascii')
        assert len(text) <= 40, repr(text)
        # TODO: Verdichtung/Korrektur
        bin_line = 't' + str(self.key) + '\x1e' + text + '\x1c' + 'y'
        return bin_line




