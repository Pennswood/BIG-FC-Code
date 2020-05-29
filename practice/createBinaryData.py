import os

def createFile():
    f = open('logfile0.bin', 'w+b')
    byte_arr = b"\x00\x02\x05\xff\xA0\x04"
    binary_format = bytearray(byte_arr)
    f.write(binary_format)
    f.close()
def seeFile():
    file = open("logfile0.bin", "rb")

    byte = file.read(1)
    while byte:
        print(byte)
        byte = file.read(1)
createFile()
seeFile()
statinfo = os.stat("logfile0.bin")
print(statinfo.st_size)