# -*- coding: UTF-8 -*-

import logging
import re

from libkne import DataLine


log = logging.getLogger(__name__)

__all__ = ["KNEAddress"]


attr_codes = \
    dict(
         new_record        = 101,
         account_number    = 102,
         name1             = 103,
         customer_number   = 104,
         zip_code          = 106,
         city              = 107,
         street            = 108,
         appellation       = 109,
         name2             = 203,
         additional_delivery_information = 701,
         nationality_key   = 702,
         language          = 703,
         phonenumber       = 710,
         faxnumber         = 711,
         emailaddress1     = 712,
         emailaddress2     = 713,
         degree            = 801,
         cellphonenumber   = 802,
         interneturl1      = 803,
         interneturl2      = 804,
        )


class KNEAddress(object):
    
    def _assert_no_unused_kw_arguments(self, kwargs):
        if len(kwargs.keys()) > 0:
            first_kw = kwargs.keys()[0]
            raise ValueError("Unknown keyword parameter '%s'" % first_kw)
    
    
    def _build_list_of_splittable_attribut_names(self):
        splittable_attribut_names = []
        for key in attr_codes:
            if key.endswith('1'):
                base_name = key[:-1]
                splittable_attribut_names.append(base_name)
        return splittable_attribut_names
    
    
    def _build_sorted_attrname_dict(self):
        code_name_tuples = []
        for name in attr_codes:
            code = attr_codes[name]
            code_name_tuples.append((code, name))
        code_name_tuples.sort()
        
        attrnames = []
        for code, name in code_name_tuples:
            attrnames.append(name)
        return attrnames
    
    def __init__(self, new_record, account_number, **kwargs):
        assert new_record in [True, False], 'new_record must in [True, False], not %s' % new_record
        assert account_number not in ['', None], 'account number must not be empty'
        self.new_record = 1
        if not new_record:
            self.new_record = 2
        self.account_number = account_number
        for name in attr_codes:
            value = kwargs.pop(name, None)
            if not hasattr(self, name):
                setattr(self, name, value)
        self._splittable_attribut_names = self._build_list_of_splittable_attribut_names()
        self._attrnames_sorted_by_key = self._build_sorted_attrname_dict()
        self._assert_no_unused_kw_arguments(kwargs)
    
    
    def _split_long_values(self, attrname, value):
        values = []
        
        max_data_length_single_line = 40
        if not isinstance(value, basestring):
            value = unicode(value)
            if len(value) > max_data_length_single_line:
                if attrname not in self._splittable_attribut_names:
                    value = value[:max_data_length_single_line]
                    base_msg = 'Line for attribute "%s" too long, cutting string: "%s..."'
                    msg = base_msg % (attrname, value)
                    log.warn(msg)
                else:
                    pass
            else:
                key = attr_codes[attrname]
                values = [(key, value)]
        return values
    
    
    def _put_values_for_basenames_into_normal_attributes(self):
        for base_name in self._splittable_attribut_names:
            
            value = getattr(self, base_name, None)
            if value not in [None, '']:
                number_of_items = 0
                for key in attr_codes:
                    regex = re.compile('^%s(\d+)$' % re.escape(base_name))
                    match = regex.search(key)
                    if match != None:
                        number_of_items += 1
                assert number_of_items > 0
                
                if not isinstance(value, basestring):
                    value = unicode(value)
                for i in range(number_of_items):
                    
                    start_index = i * 40
                    if start_index > len(value):
                        break
                    end_index = start_index + 40
                    part_value = value[start_index:end_index]
                    
                    part_key = base_name + str(i + 1)
                    existing_value = getattr(self, part_key, None)
                    if (existing_value != None) and (existing_value != part_value):
                        base_msg = 'Tried to write %s "%s" into %s but this key already has value %s'
                        msg = base_msg % (base_name, part_value, part_key, existing_value)
                        raise ValueError(msg)
                    setattr(self, part_key, part_value)
            
            
    
    
    def build_masterdata_lines(self):
        lines = []
        special_keys = ['new_record', 'account_number']
        for key in special_keys:
            value = getattr(self, key)
            assert value != None, 'No value for %s' % key
            line = DataLine(key=attr_codes[key], text=value)
            lines.append(line)
        
        self._put_values_for_basenames_into_normal_attributes()
        
        for name in self._attrnames_sorted_by_key:
            value = getattr(self, name)
            key = attr_codes[name]
            
            if value not in [None, ''] and name not in special_keys:
                #key_value_pairs = self._split_long_values(name, value)
                
                if not isinstance(value, basestring):
                    value = unicode(value)
                if len(value) > 40:
                    value = value[:40]
                    base_msg = 'Line for attribute "%s" too long, cutting string: "%s..."'
                    msg = base_msg % (name, value)
                    log.warn(msg)
                assert len(value) <= 40
                line = DataLine(key=key, text=value)
                lines.append(line)
        return lines

