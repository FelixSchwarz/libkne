# -*- coding: UTF-8 -*-


__all__ = ["KNEAddress"]

class KNEAddress(object):
    def __init__(self, **kwargs):
        for name in ['additional_delivery_information', 'appellation', 
                     'cellphonenumber', 'city', 'customer_number', 'degree', 
                     'emailaddress','faxnumber', 'interneturl', 'language', 
                     'name1', 'name2', 'nationality_key', 'phonenumber', 
                     'street', 'zip_code', ]:
            value = kwargs.pop(name, None)
            setattr(self, name, value)
        assert len(kwargs.keys()) == 0, kwargs
    
    
    def new_address_to_binary(self):
        pass

