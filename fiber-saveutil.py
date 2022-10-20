
import re
import sys
import struct
import argparse

from pathlib import Path

from sfo import Sfo
from save import GameData, SaveFile

def convert_gamedata(path_in, path_out):
    print(f"found ps4 game data -- {path_in}")
    sfo_path = Path(path_in / "../sce_sys/param.sfo")

    detail = b""
    if sfo_path.is_file():
        with open(sfo_path, "rb") as sfo:
            detail = Sfo().read(sfo).get_entry("DETAIL").value
    else:
        print(f"warn: couldn't find param.sfo for save -- {path_in}")

    pc = SaveFile()

    name_utf8 = [b"", b""]
    with open(path_in, "rb") as ps4:
        gd = GameData().read(ps4)
        name_utf8 = gd.get_block(0x1001C).full_name_utf8.strip(b'\x00').split(b' ')
        pc.header = gd.header
        ps4.seek(0, 0)
        pc.data = ps4.read()

    pc.header.lname = name_utf8[1]
    pc.header.fname = name_utf8[0]
    pc.header.desc = detail
    pc.header.lang0 = 0xFF

    path_out.mkdir(parents=True, exist_ok=True)
    with open(path_out / "DATA.DAT", "wb") as fso:
        print(f"converted gamedata -- {path_out / 'DATA.DAT'}")
        fso.write(pc.pack())

def convert_sysdata(path_in, path_out):
    print(f"found ps4 system data -- {path_in}")

    pc = SaveFile()
    pc.header = None

    with open(path_in, "rb") as ps4:
        pc.data = ps4.read()

    path_out.mkdir(parents=True, exist_ok=True)
    with open(path_out / "SYSTEM.DAT", "wb") as fso:
        print(f"converted sysdata -- {path_out / 'SYSTEM.DAT'}")
        fso.write(pc.pack())

def convert_save(path_in: Path, path_out: Path):
    with open(path_in, "rb") as fsi:
        m = struct.unpack("<I", fsi.read(4))[0]

    match m:
        case 0x2D000000: convert_gamedata(path_in, path_out)
        case 0x00000002: convert_sysdata(path_in, path_out)
        case _: print(f"error: not a ps4 save -- {path_in}")

def convert_saves(path_in: Path, path_out: Path):
    saves = [f for f in path_in.glob("./*.DAT") if f.is_file()]
    if len(saves) != 0:
        convert_save(saves[0], path_out)
        return

    saves = [f for f in path_in.glob("**/*.DAT") if f.is_file()]
    if len(saves) != 0:
        for save in saves:
            n = re.search("(DATA\d\d|SYSTEM)", save.parent.name.upper())
            convert_save(save, path_out / n[0] if n else path_out)
        return

    print(f"error: no saves were found in the provided input path -- {path_in}")

def command_convert(args):
    path_in = Path(args.path_in[0])

    if not path_in.exists():
        print("error: input path does not exist")
        return

    if not path_in.is_dir():
        print("error: input path is not a directory")
        return

    if not args.path_out:
        path_out = path_in.with_name(f"{path_in.name}--out")
    else:
        path_out = Path(args.path_out)

    if path_out.is_file():
        print("error: output path must be a directory")
        return

    convert_saves(path_in, path_out)

def dump_save(path_in, path_out, raw):
    with open(path_in, "rb") as fsi:
        m = struct.unpack("<4s", fsi.read(4))[0]

    if m != b"DATA":
        print("error: input is not a pc save")
        return

    with open(path_in, "rb") as fsi:
        print(f"parsing save -- {path_in}")
        pc = SaveFile().unpack(fsi.read())

        with open(path_out, "wb") as fso:
            print(f"dumping save -- {path_out}")
            fso.write(pc.pack(not raw, not raw))

def command_dump(args):
    path_in = Path(args.path_in[0])

    if not path_in.exists():
        print("error: input path does not exist")
        return

    if not path_in.is_file():
        print("error: input path is not a file")
        return

    if not args.path_out:
        path_out = path_in.with_name(f"{path_in.name}--out")
    else:
        path_out = Path(args.path_out)

        if path_out.is_dir():
            path_out = path_out / path_in.name
        elif path_out.parent.is_dir():
            pass
        else:
            print("error: invalid output path")
            return

    if path_in.resolve() == path_out.resolve():
        print("error: input and output path must differ")
        return

    dump_save(path_in, path_out, args.raw)

def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest = "command")
    sp_convert = subparsers.add_parser("convert", help="convert between save formats")
    sp_convert.add_argument("path_in", help="ps4 save path", nargs=1)
    sp_convert.add_argument("path_out", help="pc save path", nargs='?')
    sp_dump = subparsers.add_parser("dump", help="decrypt/encrypt pc saves")
    sp_dump.add_argument("--raw", help="don't encrypt/compress", action="store_true", default=False)
    sp_dump.add_argument("path_in", help="input pc save", nargs=1)
    sp_dump.add_argument("path_out", help="output pc save", nargs='?')
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])

    match args.command:
        case "convert": command_convert(args)
        case "dump": command_dump(args)
        case _: parser.print_help()

if __name__ == "__main__":
    main()
