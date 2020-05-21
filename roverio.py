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
            
    def read_command(self):
        if self.debug:
            a = read_buffer.pop(0)
            if a == None:
                while read_buffer.len() == 0:
                    #Wair for a command to be received
                a = read_buffer.pop(0)
            
            return a
        else:
            return self.rover_serial.read()

    """
        When debug_mode is set to True, the program will attempt to connect to the TCP port provided by fake_serial.py.
        Additionally, debug_input_buffer will hold a byte array of received/simulated commands sent from the rover.
    """
	def __init__(self, debug_mode=False, debug_input_buffer=None):
		self.debug = debug_mode
		if debug_mode:
            self.read_buffer = debug_input_buffer
			self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp_socket.connect(("localhost", ROVER_TCP_PORT))
			print("Connected to dummy serial!")
		else:
			self.rover_serial = serial.Serial("/dev/ttyS1")
			print("Created serial connection to /dev/ttyS1")

rover_serial = RoverSerial(DEBUG_SERIAL)


"""
Task: sends a response to the rover.
Input: none
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
"""
def ping():
	return rover_serial.sendByte(0x01)

"""
Task: sends all spectrometer data to the rover
Input: none
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
"""
def all_spectrometer_data():
	# TODO
	return
"""
Task: sends back a byte list of status data (in accordance to table III in rover commands) to the rover)
Input: none
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
"""
def status_request():
	# TODO
	return


def status_dump():
	# TODO
	return


def manifest_request():
	# TODO
	return


def transfer_sample():
	# TODO
	return


def clock_sync():
	# TODO
	return
