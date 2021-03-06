#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# The source code contained in this file is licensed under the MIT license.
# See LICENSE.txt in the main project directory, for more information.
# For the exact contribution history, see the git revision log.

import datetime
import StringIO

from libkne import KneWriter, AccountingLine

def _default_config():
    config = {}
    config['advisor_number'] = 1234567
    config['advisor_name'] = 'Datev eG'
    config['client_number'] = 42
    
    config['data_carrier_number'] = 1
    config['name_abbreviation'] = 'fs'
    config['date_start'] = datetime.date(2004, 02, 04)
    config['date_end'] = datetime.date(2004, 02, 29)
    return config


data_files = []
def build_new_data_fp(number_of_files):
    global data_files
    data_fp = StringIO.StringIO()
    data_files.append(data_fp)
    return data_fp


def build_kne_writer():
    data_fp_builder = build_new_data_fp
    header_fp = StringIO.StringIO()
    config = _default_config()
    writer = KneWriter(config=config, header_fp=header_fp, 
                       data_fp_builder=data_fp_builder)
    return writer


def build_posting_line():
    line = AccountingLine()
    line.transaction_volume = -115
    line.offsetting_account = 100010000
    line.record_field1 = 'Re526100910'
    line.record_field2 = '150102'
    line.date = datetime.date(day=1, month=1, year=2008)
    line.account_number = 84000000
    line.posting_text = u'AR mit UST-Automatikkonto ä'
    line.currency_code_transaction_volume = 'EUR'
    return line


def _flush_to_disk(header_fp, data_fp):
    ev = file('EV01', 'wb')
    header_fp.seek(0)
    ev.write(header_fp.read())
    ev.close()
    
    ed = file('ED00001', 'wb')
    data_fp.seek(0)
    ed.write(data_fp.read())
    ed.close()


if __name__ == '__main__':
    writer = build_kne_writer()
    line = build_posting_line()
    #writer.write_data_carrier_header()
    writer.add_posting_line(line)
    writer.finish()
    
    data_fp = data_files[0]
    _flush_to_disk(writer.header_fp, data_fp)

