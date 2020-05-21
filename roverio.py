import serial
import socket

# THE TWO BELOW VALUES ARE FOR DEBUGGING PURPOSES ONLY. THESE MEAN NOTHING TO THE PAYLOAD.
TLC_TCP_PORT = 321
ROVER_TCP_PORT = 654

#Set this to False when testing on the Beagle Bone Black
DEBUG_SERIAL = True

class RoverSerial():
	def sendByte(self, b):
		if self.debug:
			self.tcp_socket.send(b)
		else:
			self.rover_serial.write(b)

	def sendString(self, s):
		if self.debug:
			self.tcp_socket.send(s.encode('ascii'))
		else:
			self.rover_serial.write(s.encode('ascii'))

	def __init__(self, debug_mode=False):
		self.debug = debug_mode
		if debug_mode:
			self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp_socket.connect(("localhost", ROVER_TCP_PORT))
			print("Connected to dummy serial!")
		else:
			self.rover_serial = serial.Serial("/dev/ttyS1")
			print("Created serial connection to /dev/ttyS1")

rover_serial = RoverSerial(DEBUG_SERIAL)

"""
Task: checks for existing rover command and read command if it exists
Inputs: none
Returns: a 8 bit hex value for the command number sent, 0x00 for no commands sent

def read_command():


Task: writes a response to the rover.
Input: array of bytes to be sent to the rover,
with the number in index 0 to be sent first and last index sent last.
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)

def write_response(response):


Task: sends a response to the rover.
Input: none
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)

def ping():
    return write_response(hex(0x01))


Task: sends all spectrometer data to the rover
Input: none
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)

def all_spectrometer_data():


#Task: sends back a byte list of status data (in accordance to table III in rover commands) to the rover)
#Input: none
#Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)

def status_request():



def status_dump():



def manifest_request():



def transfer_sample():



def clock_sync():
"""
