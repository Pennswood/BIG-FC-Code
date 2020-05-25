import os
import pickle
#statinfo = os.stat("fun.dat")
#print(statinfo.st_size)

def create_spectrometer_file(filename, data):
    f = open(filename, 'wb')
    pickle.dump(data, f)
    return
data = [[123.42534,435.453465],[213423.2314,123214.324]]

def read_spectrometer_file(filename):
    f = open(filename, 'rb')
    return pickle.load(f)

print(read_spectrometer_file("fun.dat"))
statinfo = os.stat("fun.dat")
print(statinfo.st_size)