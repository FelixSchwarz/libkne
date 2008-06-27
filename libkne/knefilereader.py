# -*- coding: UTF-8 -*-

from StringIO import StringIO

from knereader import KneReader

__all__ = ["KneFileReader"]

class KneFileReader(KneReader):
    "Reads the data from the file system and passes them to the KneReader"
    
    def __init__(self, header_filename=None, data_filenames=None):
        assert header_filename != None
        header_fp = StringIO(file(header_filename, "rb").read())
        data_fps = []
        if data_filenames != None:
            for filename in data_filenames:
                fake_fp = StringIO(file(filename, "rb").read())
                data_fps.append(fake_fp)
        super(KneFileReader, self).__init__(header_fp=header_fp, 
                                            data_fps=data_fps)

