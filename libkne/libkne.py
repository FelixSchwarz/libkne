# -*- coding: UTF-8 -*-

import datev_encoding
datev_encoding.register()

from controlrecord import *
from postingline import *
from transactionmanager import *
from transactionfile import *
from knewriter import *
from knereader import *
from knefilereader import *



'''
Translation terms used within this library

Deutsch/German                Englisch/English
-----------------------------------------------------------------
Abrechnungsnummer             accounting number
Anwendungsinfo                application info
Anwendungsnummer              application number
Aufgezeichnete Sachkontonummernlänge
                              used general ledger account number length
Basiswährung                  base currency
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
Korrektur                     adjustment
Kostenstelle (KOST)           cost center
Mandantenendsumme             client total
Mandantennummer               client number
Namenskürzel                  name abbreviation
Primanota                     prima nota
Produktkürzel                 product abbreviation
Sachkonto                     general ledger account
Skonto                        cash discount
Stammdaten                    master data
Umsatz (einer Buchung)        transaction volume
Verdichtung                   aggregation
Versionskennung               version identifier
Versionssatz                  version record
Verwaltungssatz               control record
Vollvorlauf                   complete feed line
Währungskennzeichen           currency code
Währungskurs                  exchange rate
Wirtschaftsjahr               financial year
'''

