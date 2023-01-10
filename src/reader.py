import marshal
import time
import struct
from vm import VirtualMachine

def read_file(filename):
    with open(filename, "rb") as f:
        magic = f.read(8)
        moddate = f.read(8)
        code = marshal.load(f)
        vm = VirtualMachine(code)
        vm.run()
