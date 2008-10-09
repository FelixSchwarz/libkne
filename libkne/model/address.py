# -*- coding: UTF-8 -*-

import logging

from libkne import DataLine


log = logging.getLogger(__name__)

__all__ = ["KNEAddress"]


attr_codes = \
    dict(
         new_record=101,
         account_number = 102,
         name1=103,
         customer_number=104,
         zip_code=106,
         city=107,
         street=108,
         appellation=109,
         name2=203,
         additional_delivery_information=701,
         nationality_key=702,
         language=703,
         phonenumber=710,
         faxnumber=711,
         emailaddress=712, #713
         degree=801,
         cellphonenumber=802,
         interneturl=803, #804
        )


class KNEAddress(object):
    
    def _assert_no_unused_kw_arguments(self, kwargs):
        if len(kwargs.keys()) > 0:
            first_kw = kwargs.keys()[0]
            raise ValueError("Unknown keyword parameter '%s'" % first_kw)
    
    
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
        self._assert_no_unused_kw_arguments(kwargs)
    
    
    def build_masterdata_lines(self):
        lines = []
        special_keys = ['new_record', 'account_number']
        for key in special_keys:
            value = getattr(self, key)
            assert value != None, 'No value for %s' % key
            line = DataLine(key=attr_codes[key], text=value)
            lines.append(line)
        
        # TODO: Length check!
        for name in attr_codes:
            value = getattr(self, name)
            key = attr_codes[name]
            if value not in [None, ''] and name not in special_keys:
                if len(value) > 40:
                    value = value[:40]
                    base_msg = 'Line for attribute "%s" too long, cutting string: "%s..."'
                    msg = base_msg % (name, value)
                    log.warn(msg)
                    print msg
                line = DataLine(key=key, text=value)
                lines.append(line)
        return lines
