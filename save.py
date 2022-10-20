
import zlib
import time
import base64
import struct

from crc import calc_crc

try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
except:
    print("missing dependencies, please run:\npython -m pip install -r requirements.txt\nbefore running this script")
    exit(1)

def align(v, a):
    return (v + (a - 1)) & ~(a - 1)

class Header(object):
    def __init__(self):
        self.playtime = 0
        self.day = 0
        self.time = 0
        self.playthrough = 0
        self.difficulty = 0
        self.level = 0
        self.clear = 0
        self.fld_major = 0
        self.fld_minor = 0
        self.lang0 = 0
        self.lang1 = 0
        self.lname = b""
        self.fname = b""
        self.desc = b""

class DataBlockPlayerName(object):
    def __init__(self):
        self.full_name_utf8 = b""
        self.last_name_game = b""
        self.first_name_game = b""
        self.full_name_game = b""
        self.group_name_game = b""
        self.group_name_utf8 = b""

    def read(self, f, version):
        if version == 0x2D000000:
            return self._read_0x2D(f)
        return None

    def _read_0x2D(self, f):
        self.full_name_utf8 = f.read(56)
        self.last_name_game = f.read(20)
        self.first_name_game = f.read(20)
        self.full_name_game = f.read(40)
        self.group_name_game = f.read(25)
        self.group_name_utf8 = f.read(37)
        return self

class GameData(object):
    def __init__(self):
        self.version = 0
        self.header = None
        self.blocks = {}
        self.blocks_raw = {}

    def read(self, f):
        self.version = struct.unpack("<I", f.read(4))[0]
        if self.version == 0x2D000000:
            self._read_header_0x2D(f)
            self._read_data_0x2D(f)
        return self

    def _read_header_0x2D(self, f):
        fmt = ">2xHH2xIBBBB24s24sBB2x"
        buffer = f.read(struct.calcsize(fmt))
        p = Header()
        p.day, p.time, p.playtime, p.level, p.difficulty, p.playthrough, p.clear, \
            p.lname, p.fname, p.fld_major, p.fld_minor = struct.unpack(fmt, buffer)
        self.header = p

    def _read_data_0x2D(self, f):
        block_id, block_size = struct.unpack(">II", f.read(8))
        block_start = f.tell()

        while block_id != 0x2000:
            if block_id == 0x1001C:
                self.blocks[block_id] = DataBlockPlayerName().read(f, self.version)
            else:
                self.blocks_raw[block_id] = f.read(block_size)

            f.seek(block_start + block_size, 0)
            block_id, block_size = struct.unpack(">II", f.read(8))
            block_start = f.tell()

        self.blocks[block_id] = f.read(1)

    def get_block(self, block_id):
        if block_id in self.blocks:
            return self.blocks[block_id]
        return None

class SaveFile(object):
    CRYPT_KEY = base64.b64decode(b"3lOZS0kYSoOOtkC4c7IDfvNXnxIprUPTlUGVC3yBJF0=")

    def __init__(self):
        self.file_magic = b"DATA"
        self.file_crc = 0
        self.file_timestamp = 0
        self.file_flags = 0
        self.file_iv = None

        self.header_size = 0x1D0
        self.header_size_comp  = 0
        self.data_size = 0x30720
        self.data_size_comp = 0
        self.save_flags = 0x02110600

        self.data_crc = 0

        self.header = Header()
        self.data = None

    def decrypt(self, buffer):
        cipher = AES.new(SaveFile.CRYPT_KEY, AES.MODE_CBC, self.file_iv)
        return cipher.decrypt(buffer)

    def encrypt(self, buffer):
        cipher = AES.new(SaveFile.CRYPT_KEY, AES.MODE_CBC, self.file_iv)
        return cipher.encrypt(buffer)

    def _unpack_header(self, buffer):
        if len(buffer) < 0x190:
            self.header = None
            return

        p = Header()
        p.playtime, p.day, p.time, p.playthrough, p.difficulty, p.level, p.clear, p.fld_major, p.fld_minor, \
            p.lang0, p.lang1, lname, fname, desc = struct.unpack("<IHBBBBxBBBBB64s64s256s", buffer[:0x190])
        p.lname = lname.rstrip(b'\x00')
        p.fname = fname.rstrip(b'\x00')
        p.desc = desc.rstrip(b'\x00')

        self.header = p

    def unpack(self, buffer):
        self.file_magic, self.file_crc, self.file_timestamp, self.file_flags = struct.unpack("4s3I", buffer[:0x10])
        self.file_iv = buffer[0x10:0x20]

        if self.file_magic != b"DATA":
            return None

        file_crc = calc_crc(buffer[0x8:])
        print(f"file crc: {self.file_crc:08x} check: {file_crc:08x}")

        buffer_dec = buffer
        if self.file_flags >> 31:
            buffer_dec = buffer[:0x20] + self.decrypt(buffer[0x20:])
            self.file_flags &= ~(1 << 31)

        self.header_size, self.header_size_comp, \
        self.data_size, self.data_size_comp, \
        self.save_flags, self.data_crc = struct.unpack("<HHIIII", buffer_dec[0x20:0x34])

        if self.save_flags & 1:
            self.header = buffer_dec[0x40:self.header_size_comp]
            header = zlib.decompress(self.header)
            self.save_flags &= ~1
            data_offset = self.header_size_comp
        else:
            header = buffer_dec[0x40:self.header_size]
            data_offset = self.header_size

        self._unpack_header(header)
        data_offset = align(data_offset, 16)

        if self.save_flags & 2:
            self.data = buffer_dec[data_offset:data_offset + self.data_size_comp]
            self.data = zlib.decompress(self.data)
            self.save_flags &= ~2
        else:
            self.data = buffer_dec[data_offset:data_offset + self.data_size]

        data_crc = calc_crc(self.data)
        print(f"data crc: {self.data_crc:08x} check: {data_crc:08x}")

        return self

    def _pack_header(self):
        p = self.header
        lname = p.lname.ljust(64, b'\x00')
        fname = p.fname.ljust(64, b'\x00')
        desc = p.desc.ljust(256, b'\x00')

        return struct.pack("<IHBBBBxBBBBB64s64s256s",
            p.playtime, p.day, p.time, p.playthrough, p.difficulty, p.level, p.clear, p.fld_major, p.fld_minor,
            p.lang0, p.lang1, lname, fname, desc)

    def pack(self, compress = True, encrypt = True):
        if self.file_timestamp == 0:
            self.file_timestamp = int(time.time())
        self.data_crc = calc_crc(self.data)

        if not self.header:
            header = b""

            self.header_size = 0x40
            self.header_size_comp = 0
            hs = self.header_size
        else:
            header = self._pack_header()

            self.header_size = 0x40 + len(header)
            self.header_size_comp = 0
            hs = self.header_size
            if not self.save_flags & 1 and compress:
                header = zlib.compress(header, 9)
                self.save_flags |= 1
                self.header_size_comp = 0x40 + len(header)
                hs = self.header_size_comp

        self.data_size = len(self.data)
        self.data_size_comp = 0
        ds = self.data_size
        if not self.save_flags & 2 and compress:
            self.data = zlib.compress(self.data, 9)
            self.save_flags |= 2
            self.data_size_comp = len(self.data)
            ds = self.data_size_comp

        buffer = struct.pack("HHIIII 12x", self.header_size,
            self.header_size_comp, self.data_size, self.data_size_comp,
            self.save_flags, self.data_crc)

        buffer += header.ljust(align(hs, 16) - 0x40, b"\x00")
        buffer += self.data.ljust(align(ds, 16), b"\x00")

        self.file_iv = b"\x00" * 0x10
        if encrypt and not self.file_flags >> 31:
            self.file_flags |= 1 << 31
            self.file_iv = get_random_bytes(0x10)
            buffer = self.encrypt(buffer)

        buffer = struct.pack("<II16B", self.file_timestamp, self.file_flags, *self.file_iv) + buffer
        self.file_crc = calc_crc(buffer)

        return struct.pack("<4sI", self.file_magic, self.file_crc) + buffer
