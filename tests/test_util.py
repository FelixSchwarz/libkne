# -*- coding: UTF-8 -*-

import os
import unittest

from libkne import KneFileReader


__all__ = ['get_data_files', 'SampleDataReaderCase']


def find_filename_case_insensitively(datadir, expected_filename):
    items = {}
    for diritem in os.listdir(datadir):
        filename = os.path.join(datadir, diritem)
        if os.path.isfile(filename):
            items[diritem.lower()] = filename
    expect_filename = expected_filename.lower()
    assert expect_filename in items
    return items[expect_filename]


def get_ev_filename(datadir):
    return find_filename_case_insensitively(datadir, 'EV01')


def get_ed_filename(datadir, nr):
    return find_filename_case_insensitively(datadir, 'ED%05d' % nr)


def get_data_files(datadir, number_data_files, file_dir=None):
    if file_dir == None:
        file_dir = os.path.dirname(__file__)
    datadir = os.path.join('testdata', datadir)
    abs_dir = os.path.abspath(os.path.join(file_dir, datadir))
    header = get_ev_filename(abs_dir) 
    data_fps = []
    for i in range(1, number_data_files+1):
        data_fp = get_ed_filename(abs_dir, i)
        data_fps.append(data_fp)
    return (header, data_fps)


class SampleDataReaderCase(unittest.TestCase):
    def setUp(self, datadir, number_data_files=1, file_dir=None):
        super(SampleDataReaderCase, self).setUp()
        header, data_fps = get_data_files(datadir, number_data_files, file_dir=file_dir)
        self.reader = KneFileReader(header, data_fps)
