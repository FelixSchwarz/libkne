# -*- coding: UTF-8 -*-

import datetime

class PostingLine(object):
    def __init__(self):
        self.transaction_volume = None
        self.posting_key = None
        self.offsetting_account = None
        self.record_field1 = None
        self.record_field2 = None
        self.date = None
        self.account_number = None
        self.cash_discount = None
        self.posting_text = None
        self.eu_id = None
        self.eu_state = None
        self.vat_id = None
        self.eu_taxrate = None
        self.currency_code_transaction_volume = None
        self.base_currency_amount = None
        self.exchange_rat = None
    
    
    def _transaction_volume_to_binary(self):
        bin_volume = '%+d00' % self.transaction_volume
        return bin_volume
    
    
    def _date_to_binary(self):
        assert self.date != None
        bin_date = '%d%02d' % (self.date.day, self.date.month)
        return bin_date
    
    
    def to_binary(self):
        "Return the binary KNE format for the specified data."
        bin_line = self._transaction_volume_to_binary()
        assert self.offsetting_account != None
        bin_line += 'a' + str(self.offsetting_account)
        assert len(self.record_field1) <= 12
        bin_line += '\xbd' + self.record_field1 + '\x1c'
        assert len(self.record_field2) <= 12
        bin_line += '\xbe' + self.record_field2 + '\x1c'
        bin_line += 'd' + self._date_to_binary()
        bin_line += 'e' + str(self.account_number)
        assert len(self.posting_text) <= 30
        bin_line += '\x1e' + self.posting_text + '\x1c'
        currency_code = self.currency_code_transaction_volume
        assert len(currency_code) <= 3
        assert currency_code.upper() == currency_code
        bin_line += '\xb3' + currency_code + '\x1c'
        bin_line += 'y'
        return bin_line



product_abbreviation = "lkne"

class KneWriter(object):
    
    def __init__(self, config=None, header_fp=None, data_fp_builder=None):
        """header_fp is a file-like object which will be used to store the KNE
        header. data_fp_builder is a callable that will return a file-like 
        object when called with the number of previously retrieved fp as a an
        argument. These file-like objects will be used to store the data items 
        (transaction data or master data)."""
        self.header_fp = header_fp
        self.data_fp_builder = data_fp_builder
        self.number_data_files = -1
        
        self.posting_fp = None
        self.posting_fp_feed_written = False
        self.posting_fp_version_info_written = False
        
        self.config = self._build_config(config)
    
    
    def _build_config(self, cfg):
        config = {}
        if cfg != None:
            config.update(cfg)
        config.setdefault("data_carrier_number", 0)
        assert int(config["data_carrier_number"]) in range(0,999)
        config.setdefault("gl_account_no_length_data", 8)
        config.setdefault("gl_account_no_length_coredata", 8)
        gl_account_no_length_data = config["gl_account_no_length_data"]
        gl_account_no_length_coredata = config["gl_account_no_length_coredata"]
        assert gl_account_no_length_data in range(4,9)
        assert gl_account_no_length_coredata in range(4,9)
        assert not (gl_account_no_length_data < gl_account_no_length_coredata)
        
        assert int(config["advisor_number"]) > 0
        assert len(str(config["advisor_number"])) in range(1,8)
        config["advisor_number"] = "%07d" % int(config["advisor_number"])
        
        assert int(config["client_number"]) > 0
        assert len(str(config["client_number"])) in range(1,6)
        config["client_number"] = "%05d" % int(config["client_number"])
        
        assert len(config["name_abbreviation"]) == 2
        config["name_abbreviation"] = config["name_abbreviation"].upper()
        
        config.setdefault("accounting_number", 1)
        assert len(str(config["accounting_number"])) in range(1,5)
        config["accounting_number"] = "%04d" % int(config["accounting_number"])
        
        config.setdefault("accounting_year", datetime.date.today().year)
        assert len(str(config["accounting_year"])) == 4
        
        config.setdefault("password", "    ")
        assert len(config["password"]) == 4
        
        assert config["date_start"] != None
        assert config["date_end"] != None
        assert config["date_start"] <= config["date_end"]
        
        config.setdefault("prima_nota_page", 1)
        config["prima_nota_page"] = "%03d" % int(config["prima_nota_page"])
        assert len(config["prima_nota_page"]) == 3
        
        
        
        # should not be set from the user as this are more or less constants
        config.setdefault("version_complete_feed_line", '1')
        config.setdefault("application_number", '11') # Fibu/OPOS transaction data
        
        config.setdefault("application_info", " " * 16)
        config["application_info"] ="% -16s" % config["application_info"]
        assert len(config["application_info"]) == 16
        
        config.setdefault("input_info", " " * 16)
        config["input_info"] ="% -16s" % config["input_info"]
        assert len(config["input_info"]) == 16
        
        return config
    
    
    def write_kne_header(self):
        pass
    
    
    def _short_date(self, date):
        format = "%02d%02d%02d"
        short_year = int(str(date.year)[2:])
        return format % (date.day, date.month, short_year)
    
    
    def write_complete_feed_line(self, posting_fp_created=False):
        if not posting_fp_created:
            assert self.posting_fp == None
            self.check_posting_fp()
        start_feed_line = '\x1d'
        new_feed = '\x18'
        
        bin_line = start_feed_line + new_feed
        bin_line += self.config["version_complete_feed_line"]
        bin_line += "%03d" % self.config["data_carrier_number"]
        bin_line += self.config["application_number"]
        bin_line += self.config["name_abbreviation"]
        bin_line += self.config["advisor_number"]
        bin_line += self.config["client_number"]
        bin_line += self.config["accounting_number"] + str(self.config["accounting_year"])[2:]
        bin_line += self._short_date(self.config["date_start"])
        bin_line += self._short_date(self.config["date_end"])
        bin_line += self.config["prima_nota_page"]
        bin_line += self.config["password"]
        bin_line += self.config["application_info"]
        bin_line += self.config["input_info"]
        bin_line += 'y'
        #assert len(bin_line) == 80
        self.posting_fp.write(bin_line)
    
    
    def check_posting_fp(self):
        if self.posting_fp == None:
            self.number_data_files += 1
            self.posting_fp = self.data_fp_builder(self.number_data_files)
            self.write_complete_feed_line(posting_fp_created=True)
    
    
    def write_versioninfo_for_transaction_data(self):
        assert not self.posting_fp_version_info_written
        self.check_posting_fp()
        bin_versioninfo = '\xb5' + '1,'
        bin_versioninfo += str(self.config["gl_account_no_length_data"])
        bin_versioninfo += ','
        bin_versioninfo += str(self.config["gl_account_no_length_coredata"])
        bin_versioninfo += ','
        assert len(product_abbreviation) == 4
        assert str(product_abbreviation) == product_abbreviation
        bin_versioninfo += str(product_abbreviation)
        bin_versioninfo += '\x1c' + 'y'
        assert len(bin_versioninfo) == 13
        self.posting_fp.write(bin_versioninfo)
        self.posting_fp_version_info_written = True
    
    
    def add_posting_line(self, line):
        self.check_posting_fp()
        bin_posting_line = line.to_binary()
        self.posting_fp.write(bin_posting_line)
    
    


"""
Translation terms used within this library

Deutsch/German                Englisch/English
-----------------------------------------------------------------
Abrechnungsnummer             accounting number
Anwendungsnummer              application number
Basiswährungsbetrag           base currency amount
Belegfeld                     record field
Beraternummer                 advisor number
Bewegungsdaten                transaction data
Buchungsschlüssel             posting key
Buchungstext                  posting text
Buchungszeile                 posting line
Datenträgernummer             data carrier number
Gegenkonto                    offsetting account
Konto                         account
Mandantennummer               client number
Namenskürzel                  name abbreviation
Primanota                     prima nota
Produktkürzel                 product abbreviation
Sachkonto                     general ledger account
Skonto                        cash discount
Stammdaten                    master data
Umsatz (einer Buchung)        transaction volume
Vollvorlauf                   complete feed line
Währungskennzeichen           Währungskennzeichen
Währungskurs                  exchange rate
Wirtschaftsjahr               financial year
"""

