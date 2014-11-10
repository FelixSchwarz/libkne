# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

import re
from StringIO import StringIO
import os

from knereader import KneReader

__all__ = ['KneFileReader']

class KneFileReader(KneReader):
    'Reads the data from the file system and passes them to the KneReader'
    
    def __init__(self, header_filename=None, data_filenames=None):
        assert header_filename != None
        header_fp = StringIO(file(header_filename, 'rb').read())
        data_fps = []
        if data_filenames != None:
            for filename in data_filenames:
                fake_fp = StringIO(file(filename, 'rb').read())
                data_fps.append(fake_fp)
        super(KneFileReader, self).__init__(header_fp=header_fp, 
                                            data_fps=data_fps)
    
    
    def _list_kne_files(cls, directory_name):
        header_filename = None
        ed_regex = re.compile('^ED(\d)+$', re.IGNORECASE)
        
        nr_to_filename_dict = {}
        for item in os.listdir(directory_name):
            filename = os.path.join(directory_name, item)
            
            if os.path.isfile(filename):
                normalized_name = item.upper()
                match = ed_regex.match(normalized_name)
                if match != None:
                    nr = int(match.group(1))
                    nr_to_filename_dict[nr] = filename
                elif normalized_name.startswith('EV'):
                    header_filename = filename
        
        data_filenames = []
        sorted_keys = sorted(nr_to_filename_dict.keys())
        for nr in sorted_keys:
            filename = nr_to_filename_dict[nr]
            data_filenames.append(filename)
        return (header_filename, data_filenames)
    _list_kne_files = classmethod(_list_kne_files)
    
    
    def read_directory(cls, directory_name):
        header_filename, data_filenames = cls._list_kne_files(directory_name)
        if header_filename == None:
            raise ValueError('No control file ("EV01") found!')
        elif len(data_filenames) == 0:
            raise ValueError('No data files ("ED.....") found!')
        reader = KneFileReader(header_filename, data_filenames)
        return reader
    read_directory = classmethod(read_directory)


