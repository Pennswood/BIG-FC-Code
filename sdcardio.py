import csv
import pickle
import os
import log_file


"""
If you need to save a file please use/call functions here"
"""

"""
For internal use only!
Task: Creates a new line in the manifest catelog indicating a new file is saved
Inputs: String filename, Integer time in milliseconds since last clock sync, Integer bit size of the file, the type of tie file: 0 = spectromter, 1 = log file
0 = spectrometer data, 1 = log file, 2 = other
Returns: N/A
"""
PATH = "/home/"
#TODO: Fill in
PATH_TO_SD_CARD = ""
def append_manifest_file(fileName, time, bits, type):
    with open(PATH+"manifest.csv", 'a', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=",")
        writer.writerow(str(fileName)+","+str(time)+","+str(bits))
    return

"""
Task: After the spectrometer finishes sampling, it will send the data to this function to be saved.
Inputs: 1) a string in the format [timestamp].[file extension], 2) the 2 by 3648 data array from the spectrometer, 3) the time of the sample
Outputs: integer, 0 for success, other numbers for failure to save file (for debugging purposes)
"""
def create_spectrometer_file(filename, data, time):
    f = open(PATH_TO_SD_CARD+"/spectrometer/"+filename, 'wb')
    pickle.dump(data, f)
    statinfo = os.stat(PATH_TO_SD_CARD+"/spectrometer/"+filename)
    append_manifest_file(filename,time,statinfo.st_size*8,0) #TODO: get time? get bits?
    return
"""
Task: Returns the data array of the specific file.
Inputs: a string in the format [name].[file extension]
Outputs: a 2 by 3648 data array from the spectrometer (wavelength, intensity)
"""
def read_spectrometer_file(filename):
    f = open(PATH_TO_SD_CARD + "/spectrometer/" + filename, 'rb')
    return pickle.load(f)
"""
Task: Returns the two string of the last 2 spectrometer sample files.
Inputs: N/A
Outputs: a 2x1 String array of the last two spectrometer sample files, with the first being the most recent and the second being the next recent
The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension]}
If less than 2 files exist, then the 2nd (and possibly 1st) string will be an empty string.
"""
def last_two_spectrometer_file():
    output = ["",""]
    with open(PATH + "manifest.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[3]=="0":
                output[1] = output[0]
                output[0] = row[0]

    return output
"""
Task: Returns all strings of all spectrometer sample files.
Inputs: N/A
Returns: a nx1 String array of all n spectrometer sample files, with the first being the most recent and the last being the least recent
The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension], ...}
"""
def all_spectrometer_files():
    output = []
    with open(PATH + "manifest.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[3] == "0":
                output.append(row[0])
    return output

logFile = log_file.log_file(path = PATH_TO_SD_CARD + "/log_file/")

"""
Task: Append data into the log file. May automatically create a new file.
Inputs: Bit string data to input.
Returns: integer, 0 for success, other numbers for failure to save file (for debugging purposes)
"""
def append_log_file(data):
    logFile.append_log_file(data)
    return
"""
Task: Returns all strings of all log files.
Inputs: N/A
Returns: a nx1 String array of all n log files, with the first being the most recent and the last being the least recent
The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension], ...}
"""
def read_all_log_file():
    output = logFile.read_all_log_file()
    return output
"""
Task: Returns manifest data.
Inputs: N/A
Returns: a nx3 array of all n entries/lines in the manifest catalog, with the first being the most recent entry and the last being the least recent.
Each column will be in the format {{(String)[name].[extension],(Integer) file size in bits, (integer} milliseconds since last time sync, (integer) file type}
"""
def read_manifest():
    output = []
    with open(PATH+"manifest.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            output.append(row)

    return output