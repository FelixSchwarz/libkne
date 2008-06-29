# -*- coding: UTF-8 -*-

from datafile import DataFile

__all__ = ['KneReader']

class KneReader(object):
    
    def __init__(self, header_fp=None, data_fps=None):
        '''header_fp is a file-like object which contains the header file 
        contents. data_fps is a list of file-like objects which contain the
        real data.'''
        self.config, data_meta_information = \
            self._parse_data_carrier_header(header_fp)
        if data_fps == None:
            data_fps = []
        number_data_files = self.config['number_data_files']
        assert number_data_files == len(data_fps)
        # How can this be different?
        assert self.config['number_last_data_file'] == number_data_files
        assert len(data_fps) == int(len(data_meta_information) / 128)
        meta_info_list = self._split_meta_info_for_data(data_meta_information)
        self.files = []
        for metainfo, data_fp in zip(meta_info_list, data_fps):
            transaction_file = self._parse_data_file(metainfo, data_fp)
            self.files.append(transaction_file)
    
    
    def _parse_data_carrier_header(self, header_fp):
        config = {}
        contents = header_fp.read()
        assert (len(contents) > 0) and ((len(contents) % 128) == 0)
        config['data_carrier_number'] = int(contents[:3])
        assert ('   ' == contents[3:6])
        config['advisor_number'] = int(contents[6:13])
        config['advisor_name'] = contents[13:22].strip()
        assert (' ' == contents[22])
        config['number_data_files'] = int(contents[23:28])
        config['number_last_data_file'] = int(contents[28:33])
        assert (' '*95 == contents[33:128])
        return config, contents[128:]
    
    
    def _split_meta_info_for_data(self, data_meta_information):
        number_of_blocks = int(len(data_meta_information) / 128)
        meta_info_list = []
        for i in range(number_of_blocks):
            data = data_meta_information[(i * 128):((i + 1) * 128)]
            meta_info_list.append(data)
        return meta_info_list
    
    
    def _parse_data_file(self, binary_control_record, data_fp):
        tf = DataFile(self.config)
        tf.from_binary(binary_control_record, data_fp)
        return tf
    
    
    def get_config(self):
        return self.config
    
    
    def get_file(self, index):
        return self.files[index]
    
    
    def get_number_of_files(self):
        return len(self.files)

