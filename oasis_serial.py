import serial
import socket
import threading
import socketserver

BUFFER_SIZE = 1024

# Number of bytes that an integer (signed or unsigned) takes up.
INTEGER_SIZE = 4

# Unless Tyler tells you to, DONT touch this file. If you are getting errors in your code its probably because your code is wrong :) If you really think it's this code, message me

def DebugUDPHandlerFactory(oserial):
	class DebugUDPHandler(socketserver.BaseRequestHandler):
		def setup(self):	# This is disgusting that it actually works, but Python was designed to do this so whatever
			self.oasis_serial = oserial

		def handle(self):
			self.data = self.request[0]
			#print(type(self.data))
			#print(self.data)
			self.oasis_serial.rx_buffer_lock.acquire()
			self.oasis_serial.rx_buffer += self.data
			self.oasis_serial.rx_buffer_lock.release()
	return DebugUDPHandler

class OasisSerial():
	def sendBytes(self, b):
		if self.debug:
			self.udp_tx_socket.sendto(b, ("localhost", self.tx_port))
		else:
			self.serial_connection.write(b)

	#Sends a signed (positive or negative), big endian integer
	def sendInteger(self, i):
		b = i.to_bytes(INTEGER_SIZE, byteorder="big", signed=True)
		self.sendBytes(b)
		
	#Sends a signed (positive or negative), big endian integer
	def sendSignedInteger(self, i):
		b = i.to_bytes(INTEGER_SIZE, byteorder="big", signed=True)
		self.sendBytes(b)
		
	#Sends an unsigned (positive only), big endian integer
	def sendUnsignedInteger(self, i):
		b = i.to_bytes(INTEGER_SIZE, byteorder="big", signed=False)
		self.sendBytes(b)
		
	#This is our "ASCII encoded float" way of sending floats. This may be changed in the future.
	def sendFloat(self, f):
		s = "{:0=+4d}{:0=-3d}".format(int(f),int(abs(abs(f)-abs(int(f)))*1000)) # Please don't touch this, it took like an hour to make. Thank you.
		self.sendString(s)

	#Sends an ASCII string
	def sendString(self, s):
		self.sendBytes(s.encode('ascii'))
		
	# Returns a single byte read from the serial connection
	def readByte(self):
		return self.readBytes(1)
			
	# Returns a bytearray of length `count` read from the serial connection
	def readBytes(self, count):
		if self.debug:
			a = bytearray()
			while len(a) < count:
				self.rx_buffer_lock.acquire() # yeah, i could optimize this, but nah
				if len(self.rx_buffer) > 0:
					a.append(self.rx_buffer.pop(0))
				self.rx_buffer_lock.release()
			return a
		else:
			return self.serial_connection.read(count)
	
	# Returns a signed (positive or negative) integer read from the serial connection
	def readSignedInteger(self):
		b = self.readBytes(INTEGER_SIZE)
		return int.from_bytes(b, byteorder="big", signed=True)
	
	# Returns a signed (positive only) integer read from the serial connection
	def readUnsignedInteger(self):
		b = self.readBytes(INTEGER_SIZE)
		return int.from_bytes(b, byteorder="big", signed=False)
	
	# Returns a signed (positive or negative) integer read from the serial connection
	def readInteger(self):
		b = self.readBytes(INTEGER_SIZE)
		return int.from_bytes(b, byteorder="big", signed=True)
		
	# Returns a float read from the serial connection that was represented in our special ASCII encoded format
	def read_float(self):
		b = bytearray(self.readBytes(7))
		s = b.decode("ascii")
		l = int(s[1:4])
		r = int(s[4:7])
		f = float(l) + (0.001 * float(r))
		if s[0] == '-':
			f = f * -1.0
		return f

	"""
	When debug_mode is set to True, the program will attempt to connect to the UDP port provided by fake_serial.py.
	debug_rx_port will be the UDP port that we will listen to for incoming connections
	debug_tx_port will be the UDP port that we will connect to when sending bytes
	"""
	def __init__(self, serial_device, baud_rate=9600, debug_mode=False, debug_rx_port=0, debug_tx_port=0):
		self.debug = debug_mode
		if debug_mode:
			if debug_rx_port == 0 or debug_tx_port == 0:
				raise Exception("ERROR: You must specify a debug_rx_port and debug_tx_port when in debug serial mode!")
			
			self.tx_port = debug_tx_port
			self.rx_port = debug_rx_port
			
			self.tx_connected = False
			self.udp_tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
			self.rx_buffer = bytearray()
			self.rx_buffer_lock = threading.Lock()
			self.rx_serv = socketserver.UDPServer(("localhost", debug_rx_port), DebugUDPHandlerFactory(self))
			self.rx_thread = threading.Thread(target=self.rx_serv.serve_forever)
			self.rx_thread.daemon = True
			self.rx_thread.start()
			print("Started socketserver for dummy serial UDP port for reception (rx): " + str(debug_rx_port))
		
		else: #TODO: Set parity, stop bits, data bits
			self.serial_connection = serial.Serial(serial_device, baudrate=baud_rate)
			print("Created serial connection to " + serial_device)

	def __del__(self):
		if self.debug:
			self.rx_serv.shutdown()
		else:
			self.serial_connection.close()
