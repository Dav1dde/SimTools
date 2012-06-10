from dbpf.qfs import decompress

class File(object):
    def __init__(self, data):
        self.data = data

class CompressedFile(File):
    def __init__(self, raw):
        self.raw = raw
        self.header, self.data = decompress(raw)