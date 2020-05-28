import csv
import os
import sdcardio
import time
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
        statinfo = os.stat(self.path+'logfile'+str(self.fileCount)+'.bin')
        if statinfo.st_size>= self.length*100:
            sdcardio.append_manifest_file('logfile'+str(self.fileCount)+'.bin', time.time(), statinfo.st_size*8,1)
            #TODO: time could could change!
            self.fileCount = self.fileCount+1
        f = open(self.path+'logfile'+str(self.fileCount)+'.bin', 'a+b')
        binary_format = bytearray(byte_array)
        f.write(binary_format)
        f.close()

    def read_all_log_file(self):
        output = self.read_old_log_file()
        if len(output)+1 == self.fileCount:
            output.append('logfile'+str(self.fileCount)+'.bin')
        return output

    def __init__(self, path, log_byte_length):
        self.fileCount = len(self.read_old_log_file(path))
        self.directory = path
        self.length = log_byte_length

