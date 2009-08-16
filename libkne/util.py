# -*- coding: UTF-8 -*-

import datetime
import re

__all__ = ['APPLICATION_NUMBER_TRANSACTION_DATA', 
           'APPLICATION_NUMBER_MASTER_DATA', '_short_date', 
           'assert_match', 'assert_true', 
           'product_abbreviation', 'get_number_of_decimal_places',
           'is_debtor_account', 'parse_short_date', 'parse_number', 
           'parse_number_field', 'parse_optional_number_field', 
           'parse_optional_string_field', 'parse_string', 'parse_string_field', 
           'replace_unencodable_characters', 'short_date_to_binary', ]

APPLICATION_NUMBER_TRANSACTION_DATA = 11
APPLICATION_NUMBER_MASTER_DATA      = 13

product_abbreviation = 'lkne'

def _short_date(date):
    return short_date_to_binary(date)

replacement_table_for_non_datev_characters = {
    # General
    
    # France
    u'é': 'e', u'è': 'e', u'á': 'a', u'à': 'a', u'î': 'i',
    
    # Turkey
    u'ç': 'c',
    
    # Polish, Czech, Slovak
    u'ó': 'o',
    
    # KNE ASCII does not know the '~' character. Probably it is used mostly for
    # URLs where it can be encoded using the hexadecimal ASCII value.
    u'~': '%7E',
    
#    
#    u'': '', u'': '', u'': '', u'': '', u'': '', u'': '',
}

# ------------------------------------------------------------------------------
sciformat_regex = re.compile('^(-?\d+(?:\.\d+)?)(?:E(\+\d+))?$')
def append_zeroes(old_number, dot_index, new_dot_index):
    numbers_after_dot = len(old_number) - dot_index
    new_number = old_number[:dot_index] + old_number[(dot_index+1):]
    if float(old_number) > 0:
        additional_zeroes = new_dot_index - numbers_after_dot
    else:
        additional_zeroes = new_dot_index - numbers_after_dot - 1
    return new_number + ('0' * additional_zeroes)


def format_to_normal(dec):
    decstr = str(dec.normalize())
    match = sciformat_regex.match(decstr)
    assert match != None, decstr
    number, exponent = match.groups()
    if exponent == None:
        return number
    
    exponent = int(exponent)
    assert exponent > 0
    if '.' not in number:
        return number + ('0' * exponent)
    dot_index = number.index('.')
    new_dot_index = dot_index + exponent
    assert new_dot_index >= len(number)
    return append_zeroes(number, dot_index, new_dot_index)


def get_number_of_decimal_places(number_string):
    if '.' in number_string:
        dot_index = number_string.index('.')
        return len(number_string) - dot_index - 1
    return 0
# ------------------------------------------------------------------------------

def assert_match(expected, real_data, additional_data=None):
    '''Asserts that expected is equal to real_data. Raises a ValueError if this
    assumption is not True. If additional_data is != None, repr() of this value
    will be appended on the exception.
    This method won't be optimized out like assert statements in pyo files.'''
    if not (expected == real_data):
        msg = '%s != %s' % (repr(expected), repr(real_data))
        if additional_data != None:
            msg += ' (%s)' % repr(additional_data)
        raise ValueError(msg)


def assert_true(condition, additional_data=None):
    '''Asserts that condition is True. Raises a ValueError otherwise. If 
    additional_data is != None, repr() of this value will be appended on the 
    exception.
    This method won't be optimized out like assert statements in pyo files.'''
    assert_match(True, condition, additional_data=additional_data)


def is_debtor_account(account_nr, general_ledger_account_number_length=4):
    '''Return True if the account_nr is a debtor account number in the DATEV
    accounting plain SKR03/04, else False.'''
    min_debtor_account_nr = 10 ** (general_ledger_account_number_length - 1)
    if min_debtor_account_nr <= account_nr:
        max_debtor_account_nr = 7 * min_debtor_account_nr - 1
        if account_nr <= max_debtor_account_nr:
            return True
    return False


def parse_short_date(binary_data):
    '''Parses a short date with the format 'DDMMJJ' into a real datetime.date.
    Years lower than 60 are interpreted as 19xx, all other years as 20xx.'''
    assert_match(6, len(binary_data), binary_data)
    assert len(binary_data) == 6, len(binary_data)
    day = int(binary_data[:2])
    month = int(binary_data[2:4])
    year = int(binary_data[4:])
    if year < 60:
        year += 2000
    else:
        year += 1900
    return datetime.date(year, month, day)


def parse_number(data, start_index, max_end_index, restrict_number_length=None):
    '''Reads all digits from start_index until either a non-digit character is
    read or the digit on position max_end_index was read successfully. Returns
    the read number (as int) and the last index where a digit was read.
    If restrict_number_length is specified, the read number string will be cut
    after restrict_number_length before removing leading zeroes (if any).'''
    string_number = ''
    for i in range(start_index, max_end_index+1):
        if data[i] not in map(str, range(10)):
            break
        string_number += data[i]
    end_index = start_index + len(string_number) - 1
    if restrict_number_length != None and len(string_number) > restrict_number_length:
        print 'restricting "%s" to %d characters (is %d bytes long)' % (string_number, restrict_number_length, len(string_number))
        string_number = string_number[0:restrict_number_length]
    return (int(string_number), end_index)


def parse_string(data, start_index, max_end_index=None, stop_character='\x1c'):
    '''Reads all characters until the stop character (default '\x1c') is read 
    or max_end_index is reached.'''
    read_string = ''
    if max_end_index != None:
        for i in range(start_index, max_end_index+1+1):
            if data[i] == stop_character:
                break
            read_string += data[i]
    else:
        i = start_index
        while i < len(data) and data[i] != stop_character:
            read_string += data[i]
            i += 1
    assert_match(stop_character, data[i], data[i])
    end_index = start_index + len(read_string) - 1 + 1
    return (read_string, end_index)


def parse_optional_string_field(data, first_character, start, max_characters):
    if first_character == data[start]:
        value, end_index = parse_string(data, start+1, start+max_characters)
        return (value, end_index)
    return (None, start-1)


def parse_string_field(data, first_character, start, max_characters):
    assert_match(first_character, data[start])
    value, end_index = parse_string(data, start+1, start+max_characters)
    return (value, end_index)


def parse_number_field(data, first_character, start, max_digits, restrict_number_length=None):
    assert first_character == data[start], repr(first_character) + ' != ' + repr(data[start])
    value, end_index = parse_number(data, start+1, start + max_digits,
                                    restrict_number_length=restrict_number_length)
    return (value, end_index)


def parse_optional_number_field(data, first_character, start, max_digits):
    '''Parses an optional numeric field (only parsed if first_character is
    present in data[start]). Returns a tuple (value, last_index_used) where
    value is None if the field was not present.'''
    if first_character == data[start]:
        value, end_index = parse_number(data, start+1, start + max_digits)
        return (value, end_index)
    return (None, start-1)


def replace_unencodable_characters(value):
    '''Replaces all characters which can not be represented in the (extended)
    ASCII encoding defined by DATEV by counterparts which look similar.'''
    for key in replacement_table_for_non_datev_characters:
        value = value.replace(key, replacement_table_for_non_datev_characters[key])
    return value


def short_date_to_binary(date):
    format = '%02d%02d%02d'
    short_year = int(str(date.year)[2:])
    return format % (date.day, date.month, short_year)


