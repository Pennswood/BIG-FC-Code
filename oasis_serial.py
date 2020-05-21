import serial
import socket

# The two value below are for debugging purposes only, they mean nothing to the TLC or BBB
TLC_TCP_PORT = 321
ROVER_TCP_PORT = 654

class OasisSerial():
	def sendBytes(self, b):
		if self.debug:
			self.tcp_socket.send(b)
		else:
			self.serial_connection.write(b)

	def sendInteger(self, i):
		b = i.to_bytes(2, byteorder="big")
		self.sendBytes(b)
		
	#This is our "ASCII encoded float" way of sending floats. This may be changed in the future.
	def sendFloat(self, f):
		s = "{:0=+4d}{:0=-3d}".format(int(f),int(abs(abs(f)-abs(int(f)))*1000)) # Please don't touch this, it took like an hour to make. Thank you.
		self.sendString(s)

	def sendString(self, s):
		self.sendBytes(s.encode('ascii'))

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
	def __init__(self, serial_device, debug_mode=False, debug_input_buffer=None, debug_port=0):
		self.debug = debug_mode
		if debug_mode:
			if debug_port == 0:
				raise Exception("ERROR: You must specify a debug_port when in debug serial mode!")
				
			self.read_buffer = debug_input_buffer
			self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp_socket.connect(("localhost", debug_port))
			print("Connected to dummy serial TCP port " + str(debug_port))
		else:
			self.serial_connection = serial.Serial(serial_device)
			print("Created serial connection to " + serial_device)

	def __del__(self):
		if self.debug:
			self.tcp_socket.close()
		else:
			self.serial_connection.close()
