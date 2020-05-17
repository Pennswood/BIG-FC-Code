"""
Task: checks for existing rover command and read command if it exists
Inputs: none
Returns: an integer value for the command number sent, or -1 for no commands sent
"""
def read_command():

"""
Task: writes a response to the rover.
Input: array of hex numbers to be sent to the rover,
with the number in index 1 to be sent first and last index sent last.
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
"""
def write_response(response):


"""
Task: sends a response to the rover.
Input: none
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
"""
def ping():
    return write_response(hex(0x01))

"""
"""
def all_spectrometer_data():

"""
"""
def status_request():

"""
"""
def status_dump():

"""
"""
def manifest_request():

"""
"""
def transfer_sample():

"""
"""
def clock_sync():
