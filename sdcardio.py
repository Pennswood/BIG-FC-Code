import csv
import pickle
import os
import log_file


class sdcard():
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

    def append_manifest_file(self,fileName, time, bits, type):
        with open(self.path+"manifest.csv", 'a', newline='') as csvFile:
            writer = csv.writer(csvFile, delimiter=",")
            writer.writerow(str(fileName)+","+str(time)+","+str(bits))
        return

    """
    Task: After the spectrometer finishes sampling, it will send the data to this function to be saved.
    Inputs: 1) a string in the format [timestamp].[file extension], 2) the 2 by 3648 data array from the spectrometer, 3) the time of the sample
    Outputs: integer, 0 for success, other numbers for failure to save file (for debugging purposes)
    """
    def create_spectrometer_file(self,filename, data, time):
        f = open(self.path_to_sd_card+"/spectrometer/"+filename, 'wb')
        pickle.dump(data, f)
        statinfo = os.stat(self.path_to_sd_card+"/spectrometer/"+filename)
        self.append_manifest_file(filename,time,statinfo.st_size*8,0) #TODO: get time? get bits?
        return
    """
    Task: Returns the data array of the specific file.
    Inputs: a string in the format [name].[file extension]
    Outputs: a 2 by 3648 data array from the spectrometer (wavelength, intensity)
    """
    def read_spectrometer_file(self,filename):
        f = open(self.path_to_sd_card + "/spectrometer/" + filename, 'rb')
        return pickle.load(f)
    """
    Task: Returns the two string of the last 2 spectrometer sample files.
    Inputs: N/A
    Outputs: a 2x1 String array of the last two spectrometer sample files, with the first being the most recent and the second being the next recent
    The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension]}
    If less than 2 files exist, then the 2nd (and possibly 1st) string will be an empty string.
    """
    def last_two_spectrometer_file(self):
        output = ["",""]
        with open(self.path + "manifest.csv", newline='') as csvfile:
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
    def all_spectrometer_files(self):
        output = []
        with open(self.path + "manifest.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if row[3] == "0":
                    output.append(row[0])
        return output


    """
    Task: Append data into the log file. May automatically create a new file.
    Inputs: Bit string data to input.
    log_reason: 0 = regular time log, 1 = command sent, 2 = new error, 3 = error resolved
    Returns: integer, 0 for success, other numbers for failure to save file (for debugging purposes)
    """
    def append_log_file(self,rover,time, INTEGER_SIZE, states_laser,spectrometer,temperature, duty_cycles,active_errors, status, log_reason):
        data = int(time).to_bytes(INTEGER_SIZE, byteorder="big", signed=True) + \
        rover.get_status_array(states_laser, spectrometer.states_spectrometer, temperature,
                               duty_cycles(), active_errors, status)
        if log_reason == 0:
            data = data + b'\x00'
        elif log_reason == 1:
            data = data + b'\x01'
        elif log_reason == 2:
            data = data + b'\x02'
        elif log_reason == 3:
            data = data + b'\x03'
        elif log_reason == 4:
            data = data + b'\x04'
        elif log_reason == 5:
            data = data + b'\x05'
        elif log_reason == 6:
            data = data + b'\x06'
        elif log_reason == 7:
            data = data + b'\x07'
        elif log_reason == 8:
            data = data + b'\x08'
        elif log_reason == 9:
            data = data + b'\x09'
        self.logFile.append_log_file(data)
        return
    """
    Task: Returns all strings of all log files.
    Inputs: N/A
    Returns: a nx1 String array of all n log files, with the first being the most recent and the last being the least recent
    The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension], ...}
    """
    def read_all_log_file(self):
        output = self.logFile.read_all_log_file()
        return output
    """
    Task: Returns manifest data.
    Inputs: N/A
    Returns: a nx3 array of all n entries/lines in the manifest catalog, with the first being the most recent entry and the last being the least recent.
    Each column will be in the format {{(String)[name].[extension],(Integer) file size in bits, (integer} milliseconds since last time sync, (integer) file type}
    """
    def read_manifest(self):
        output = []
        with open(self.path+"manifest.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                output.append(row)

        return output
    def __init__(self, path, path_to_sd_card,log_byte_length):
        self.path = path
        self.path_to_sd_card = path_to_sd_card
        self.logFile = log_file.log_file(sdcard=self, path=path, path_to_log=path_to_sd_card + "/log_file/", log_byte_length=log_byte_length)