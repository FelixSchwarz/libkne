# -*- coding: UTF-8 -*-
''' Datev Character Mapping Codec

as defined by DATEV e.G. in SELF 'Schnittstellen-Entwicklungsleitfaden',
version 3.3 (March 2007).

Written by Felix Schwarz (felix.schwarz@oss.schwarz.eu).

(c) Copyright 2008 Felix Schwarz.
'''

# ------------------------------------------------------------------------------
# verbatim copy from Python's (version 2.4.4) encodings/cp437.py 
# However, I don't think the code below is copyrightable because it's merely an
# interface definition.
import codecs

### Codec APIs
class Codec(codecs.Codec):
    def encode(self,input,errors='strict'):
        return codecs.charmap_encode(input,errors,encoding_map)

    def decode(self,input,errors='strict'):
        return codecs.charmap_decode(input,errors,decoding_map)

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

### encodings module API
def getregentry():
    return (Codec().encode,Codec().decode,StreamReader,StreamWriter)

decoding_map = codecs.make_identity_dict(range(0x20,0x5b))
decoding_map.update(codecs.make_identity_dict(range(0x5f,0x7b)))

# ------------------------------------------------------------------------------
# DATEV specifies its character set (named 'ASCII table') on Fach 3, page 33.
# The character set is somewhat similar to CP437 [1] but contains some 
# modifications as the Euro glyph.
#
# This special codec was written because
#   1. DATEV does not allow all characters valid in CP437
#   2. Python's cp437 encoding does not map the unicode paragraph sign (§, 0x47)
#      to 0x15 in CP437 for an unknown reason. Maybe because values in range 
#      0 to 0x20 are subject to dual use as ASCII control characters and 
#      graphical output (according to Wikipedia) and the automatic generation
#      script uses the ASCII control characters for backward-mapping.
#   3. The unicode Euro glyph (€, 0x20ac) is not present in all modifications/
#      variants/successors of the CP437 codec I cound find.
#   4. A custom codec does input validation too because characters not defined
#      here will cause an Exception to be thrown.
#
# [1] http://en.wikipedia.org/wiki/Code_page_437#Characters


### Decoding Map
decoding_map.update({
        0x0015: 0x00a7, # paragraph sign
        0x0081: 0x00fc, # ü
        0x0084: 0x00e4, # ä
        0x008E: 0x00c4, # Ä
        0x0094: 0x00f6, # ö
        0x0099: 0x00d6, # Ö
        0x009a: 0x00dc, # Ü
        0x00e1: 0x00df, # ß
        0x00f9: 0x2219, # ∙
        0x00fe: 0x20ac, # Euro sign
})

### Encoding Map
encoding_map = codecs.make_encoding_map(decoding_map)

def register():
    '''Register this codec in the standard Python codec registry. Afterwards you
    can decode/encode strings using the codec name 'datev_ascii'.'''
    def is_datev(codec_name):
        if codec_name == 'datev_ascii':
            return getregentry()
        return None
    codecs.register(is_datev)
