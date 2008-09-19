# -*- coding: UTF-8 -*-

from data_line import *
from knereader import *
from knefilereader import *
from knefilewriter import *
from knewriter import *
from postingline import *

import datev_encoding
datev_encoding.register()

'''
Some constants used in the KNE format

application info
  11    transaction data for financial accounting
  13    master data (financial accounting)


posting keys 
   50-59   reserved for custom use

(first digit, amendment key - SELF Fach 4, S. 18)
   2    Generalumkehrschlüssel
   3    Generalumkehr bei aufzuteilender VSt.
(zu Berichtigungsschlüssel 9)
   4    treat transaction volume as net value (no salex tax computation on 
        all automatic accounts of this transaction)
   5    custom sales tax key
   7    Generalumkehrschlüssel (70 – 79) für ind. USt.-Schlüssel
   8    Generalumkehr bei Aufhebung der Automatik
(zu Berichtigungsschlüssel4)
   9    splitted input tax

(second digit, tax key - SELF Fach 4, S. 11)
   1    no sales tax (with input tax deduction)
   2    7% sales tax
   3    19% sales tax
   4    reserved
   5    16% sales tax
   6    reserved
   7    16% input tax
   8    7% input tax
   9    19% input tax


Translation terms used within this library

Deutsch/German                Englisch/English
-----------------------------------------------------------------
Abrechnungsnummer             accounting number
Anwendungsinfo                application info
Anwendungsnummer              application number
Aufgezeichnete Sachkontonummernlänge
                              used general ledger account number length
Automatikkonto                automatic account
Basiswährung                  base currency
Basiswährungsbetrag           base currency amount
Belegfeld                     record field
Beraternummer                 advisor number
Berichtigungsschlüssel        amendment key
Bewegungsdaten                transaction data
Buchungsschlüssel             posting key
Buchungstext                  posting text
Buchungszeile                 posting line
Datenträgerkennsatz           data carrier header
Datenträgernummer             data carrier number
Finanzbuchhaltung (Fibu)      financial accounting
Gegenkonto                    offsetting account
Gespeicherte Sachkontonummernlänge
                              stored general ledger account number length
Kennziffer                    key
Konto                         account
Korrektur                     adjustment
Kostenstelle (KOST)           cost center
Mandantenendsumme             client total
Mandantennummer               client number
Namenskürzel                  name abbreviation
Nationalitätenkennzeichen     nationality key
Netto                         net
Personenkonto                 sub-ledger account
Primanota                     prima nota
Produktkürzel                 product abbreviation
Sachkonto                     general ledger account
Skonto                        cash discount
Stammdaten                    master data
Steuerschlüssel               tax key
Umsatz (einer Buchung)        transaction volume
Umsatzsteuer                  sales tax
Verdichtung                   aggregation
Versionskennung               version identifier
Versionssatz                  version record
Verwaltungssatz               control record
Vollvorlauf                   complete feed line
Vorsteuer                     input tax
Währungskennzeichen           currency code
Währungskurs                  exchange rate
Wirtschaftsjahr               financial year
Zustellzusatz                 additional delivery information
Zwischensumme                 subtotal
'''

