"""
If you need to save a file please use/call functions here"
"""

"""
For internal use only!
Task:
"""
def append_manifest_file(data):
    #TODO
    return

"""
Task: After the spectrometer finishes sampling, it will send the data to this function to be saved.
Inputs: 1) a string in the format [timestamp].[file extension], and 2) the 2 by 3648 data array from the spectrometer
Outputs: integer, 0 for success, other numbers for failure to save file (for debugging purposes)
"""
def create_spectrometer_file(filename, data):
    #TODO
    reutrn
"""
Task: Returns the data array of the specific file.
Inputs: a string in the format [name].[file extension]
Outputs: a 2 by 3648 data array from the spectrometer (wavelength, intensity)
"""
def read_spectrometer_file(filename):
    #TODO
    return
"""
Task: Returns the two string of the last 2 spectrometer sample files.
Inputs: N/A
Outputs: a 2x1 String array of the last two spectrometer sample files, with the first being the most recent and the second being the next recent
The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension]}
"""
def last_two_spectrometer_file():
    #TODO
    return
"""
Task: Returns all strings of all spectrometer sample files.
Inputs: N/A
Returns: a nx1 String array of all n spectrometer sample files, with the first being the most recent and the last being the least recent
The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension], ...}
"""
def all_spectrometer_files():
    # TODO
    return
"""
Task: Append data into the log file. May automatically create a new file.
Inputs: Bit string data to input.
Returns: integer, 0 for success, other numbers for failure to save file (for debugging purposes)
"""
def append_log_file(data):
    # TODO
    return
"""
Task: Returns all strings of all log files.
Inputs: N/A
Returns: a nx1 String array of all n log files, with the first being the most recent and the last being the least recent
The string will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension], ...}
"""
def read_all_log_file():
    # TODO
    return
"""
Task: Returns manifest data.
Inputs: N/A
Returns: a nx3 array of all n entries/lines in the manifest catalog, with the first being the most recent entry and the last being the least recent.
Each column will be in the format {{(String)[name].[extension],(Integer) file size in bits, (integer} milliseconds since last time sync}
"""
def read_manifest():
    # TODO
    return