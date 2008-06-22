# -*- coding: UTF-8 -*-

import datetime
from decimal import Decimal
import math
import re
from StringIO import StringIO

import datev_encoding
datev_encoding.register()

from controlrecord import ControlRecord
from postingline import PostingLine
from transactionmanager import TransactionManager
from transactionfile import TransactionFile
from knewriter import KneWriter
from knereader import KneReader
from knefilereader import KneFileReader


product_abbreviation = "SELF"


"""
Translation terms used within this library

Deutsch/German                Englisch/English
-----------------------------------------------------------------
Abrechnungsnummer             accounting number
Anwendungsnummer              application number
Aufgezeichnete Sachkontonummernlänge
                              used general ledger account number length
Basiswährungsbetrag           base currency amount
Belegfeld                     record field
Beraternummer                 advisor number
Bewegungsdaten                transaction data
Buchungsschlüssel             posting key
Buchungstext                  posting text
Buchungszeile                 posting line
Datenträgerkennsatz           data carrier header
Datenträgernummer             data carrier number
Gegenkonto                    offsetting account
Gespeicherte Sachkontonummernlänge
                              stored general ledger account number length
Konto                         account
Mandantenendsumme             client total
Mandantennummer               client number
Namenskürzel                  name abbreviation
Primanota                     prima nota
Produktkürzel                 product abbreviation
Sachkonto                     general ledger account
Skonto                        cash discount
Stammdaten                    master data
Umsatz (einer Buchung)        transaction volume
Versionskennung               version identifier
Versionssatz                  version record
Verwaltungssatz               control record
Vollvorlauf                   complete feed line
Währungskennzeichen           currency code
Währungskurs                  exchange rate
Wirtschaftsjahr               financial year
"""

