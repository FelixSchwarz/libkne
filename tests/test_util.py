# -*- coding: UTF-8 -*-

import os
import unittest

from libkne import KneFileReader


__all__ = ["get_data_files", "SampleDataReaderCase"]

def get_data_files(datadir, number_data_files):
    file_dir = os.path.dirname(__file__)
    datadir = os.path.join('testdata', datadir)
    abs_dir = os.path.abspath(os.path.join(file_dir, datadir))
    header = os.path.join(abs_dir, 'EV01')
    data_fps = []
    for i in range(1, number_data_files+1):
        data_fp = os.path.join(abs_dir, 'ED%05d' % i)
        data_fps.append(data_fp)
    return (header, data_fps)


class SampleDataReaderCase(unittest.TestCase):
    def setUp(self, datadir, number_data_files=1):
        super(SampleDataReaderCase, self).setUp()
        header, data_fps = get_data_files(datadir, number_data_files)
        self.reader = KneFileReader(header, data_fps)
