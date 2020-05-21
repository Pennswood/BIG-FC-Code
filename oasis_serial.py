import serial
import socket

# The two value below are for debugging purposes only, they mean nothing to the TLC or BBB
TLC_TCP_PORT = 321
ROVER_TCP_PORT = 654

class OasisSerial():
	def sendByte(self, b):
		if self.debug:
			self.tcp_socket.send(b)
		else:
			self.serial_connection.write(b)

	def sendString(self, s):
		if self.debug:
			self.tcp_socket.send(s.encode('ascii'))
		else:
			self.serial_connection.write(s.encode('ascii'))

	def read_command(self):
		if self.debug:
			while len(self.read_buffer) == 0:
				a = ''	#Wait for a command to be received
			a = self.read_buffer.pop(0)   
			return a
		else:
			return self.serial_connection.read()

	"""
	When debug_mode is set to True, the program will attempt to connect to the TCP port provided by fake_serial.py.
	Additionally, debug_input_buffer will hold a byte array of received/simulated commands sent from the rover.
	"""
	def __init__(self, debug_mode=False, debug_input_buffer=None, debug_port=0):
		self.debug = debug_mode
		if debug_mode:
			if debug_port == 0:
				raise Exception("ERROR: You must specify a debug_port when in debug serial mode!")
				
			self.read_buffer = debug_input_buffer
			self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp_socket.connect(("localhost", debug_port))
			print("Connected to Rover dummy serial!")
		else:
			self.serial_connection = serial.Serial("/dev/ttyS1")
			print("Created serial connection to /dev/ttyS1")

	def __del__(self):
		if self.debug:
			self.tcp_socket.close()
		else:
			self.serial_connection.close()
