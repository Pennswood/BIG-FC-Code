import csv
import os
import time
from threading import Timer,Thread,Event
class log_file():
    def read_old_log_file(self):
        output = []
        with open(self.path + "manifest.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if row[3] == "1":
                    output.append(row[0])
        return output

    def append_log_file(self, byte_array):
        try:
            statsize = os.stat(self.path_to_log+'logfile'+str(self.fileCount)+'.bin').st_size
        except: #No file created
            statsize = 0
        print(statsize)
        if statsize>= self.length*100:
            self.sdcard.append_manifest_file('logfile'+str(self.fileCount)+'.bin', int(time.time()), statsize,1)
            #TODO: time could could change!
            self.fileCount = self.fileCount+1
        f = open(self.path_to_log+'logfile'+str(self.fileCount)+'.bin', 'a+b')
        binary_format = bytearray(byte_array)
        f.write(binary_format)
        f.close()

    def read_all_log_file(self):
        output = self.read_old_log_file()
        if len(output)+1 == self.fileCount:
            output.append('logfile'+str(self.fileCount)+'.bin')
        return output

    def __init__(self, sdcard,path,path_to_log, log_byte_length):
        self.path = path
        self.sdcard = sdcard
        self.path_to_log = path_to_log
        self.fileCount = len(self.read_old_log_file())
        self.length = log_byte_length
