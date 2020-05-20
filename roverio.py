import serial

def setup_serial():
	global roverSerial, tlcSerial
	roverSerial = serial.Serial("/dev/ttyS1")

"""
Task: checks for existing rover command and read command if it exists
Inputs: none
Returns: a 8 bit hex value for the command number sent, 0x00 for no commands sent
"""
def read_command():

"""
Task: writes a response to the rover.
Input: array of bytes to be sent to the rover,
with the number in index 0 to be sent first and last index sent last.
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
Task: sends all spectrometer data to the rover
Input: none
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
"""
def all_spectrometer_data():

"""
Task: sends back a byte list of status data (in accordance to table III in rover commands) to the rover)
Input: none
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
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
