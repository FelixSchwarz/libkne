# -*- coding: UTF-8 -*-

import datetime
import re

__all__ = ["_short_date", "product_abbreviation", "get_number_of_decimal_places",
           "parse_short_date", "parse_number"]

product_abbreviation = "SELF"

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


def parse_number(data, start_index, max_end_index):
    '''Reads all digits from start_index until either a non-digit character is
    read or the digit on position max_end_index was read successfully. Returns
    the last index where a digit was read.'''
    string_number = ''
    for i in range(start_index, max_end_index+1):
        if data[i] not in map(str, range(10)):
            break
        string_number += data[i]
    end_index = start_index + len(string_number) - 1
    return (int(string_number), end_index)

