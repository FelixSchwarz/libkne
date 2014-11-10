# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

from libkne.util import assert_match, parse_string_field

__all__ = ['CustomInfoRecord']


class CustomInfoRecord(object):
    
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
    
    
    @classmethod
    def from_binary(cls, binary_data, start_index):
        data = binary_data[start_index:]
        custom_info = cls()
        custom_info.key, end_index = parse_string_field(data, '\xb7', 0, 20)
        custom_info.value, end_index = parse_string_field(data, '\xb8', 
                                                          end_index+1, 210)
        assert_match('y', data[end_index+1])
        return (custom_info, start_index + end_index + 1)
    
    
    def to_binary(self):
        'Return the binary KNE format for this info record.'
        assert self.key != None
        assert self.value != None
        bin_line = '\xb7' + str(self.key) + '\x1c'
        bin_line += '\xb8' + str(self.value) + '\x1c'
        bin_line += 'y'
        return bin_line

