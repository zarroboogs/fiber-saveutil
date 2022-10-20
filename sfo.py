
import struct

def read_cstring(f):
    s = b''
    while True:
        c = f.read(1)
        if not c or c == b'\x00':
            break
        s += c
    return s

class SfoEntry(object):
    FMT = '<HHIII'

    def __init__(self):
        self.key_offset = None
        self.format = None
        self.size = None
        self.max_size = None
        self.data_offset = None

        self.key = None
        self.value = None

    def read(self, f):
        buffer = f.read(struct.calcsize(SfoEntry.FMT))
        self.key_offset, self.format, self.size, self.max_size, self.data_offset = struct.unpack(SfoEntry.FMT, buffer)

        return self

class Sfo(object):
    FMT = '<4sIIII'

    def __init__(self):
        self.magic = None
        self.version = None
        self.key_table_offset = None
        self.data_table_offset = None
        self.num_entries = None

        self.entries = None
        self.entry_map = None

    def read(self, f):
        start_offset = f.tell()

        buffer = f.read(struct.calcsize(Sfo.FMT))
        self.magic, self.version, self.key_table_offset, self.data_table_offset, self.num_entries = struct.unpack(Sfo.FMT, buffer)

        self.entries = []
        for _ in range(self.num_entries):
            entry = SfoEntry().read(f)
            assert entry.max_size >= entry.size
            self.entries.append(entry)

        self.entry_map = {}
        for entry in self.entries:
            f.seek(start_offset + self.key_table_offset + entry.key_offset)
            entry.key = read_cstring(f).decode('ascii')
            f.seek(start_offset + self.data_table_offset + entry.data_offset)
            entry.value = f.read(entry.max_size)[:entry.size]
            self.entry_map[entry.key] = entry

        return self

    def get_entry(self, key):
        if key in self.entry_map:
            return self.entry_map[key]
        return None
