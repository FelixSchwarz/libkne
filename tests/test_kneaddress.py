# -*- coding: UTF-8 -*-

import unittest

from libkne.model import KNEAddress


class TestKNEAddress(unittest.TestCase):
    def test_cut_long_strings(self):
        kneaddr = KNEAddress(True, 10001)
        kneaddr.degree = 'Dipl.-Inform. (Univ) / Foo Bar Master Manager (BA)'
        lines = kneaddr.build_masterdata_lines()
        self.assertEqual(3, len(lines))


