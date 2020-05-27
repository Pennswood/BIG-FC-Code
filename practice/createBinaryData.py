import os

def createFile():
    f = open('my_file.bin', 'w+b')
    byte_arr = b"\x00\x02\x05\xff\xA0\x04"
    binary_format = bytearray(byte_arr)
    f.write(binary_format)
    f.close()
def seeFile():
    file = open("my_file.bin", "rb")

    byte = file.read(1)
    while byte:
        print(byte)
        byte = file.read(1)
createFile()
seeFile()
statinfo = os.stat("my_file.bin")
print(statinfo.st_size)