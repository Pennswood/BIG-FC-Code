import serial
import socket
import os
import zlib
import hashlib
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

			self.oasis_serial.rx_buffer_lock.acquire()
			if self.oasis_serial.rx_print_prefix:
				print(self.oasis_serial.rx_print_prefix + str(self.data))
			self.oasis_serial.rx_buffer += self.data
			self.oasis_serial.rx_buffer_lock.release()
	return DebugUDPHandler
	
def timeoutTimer(oserial):
	print("Timeout")
	oserial.read_timeout = True

class OasisSerial():
	def in_waiting(self):
		if self.debug:
			self.rx_buffer_lock.acquire()
			c = len(self.rx_buffer)
			self.rx_buffer_lock.release()
			return c
		else:
			return self.serial_connection.in_waiting

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
		
	# Returns a single byte read from the serial connection. Returns None if timed out reading the byte
	def readByte(self):
		b, timeout = self.readBytes(1)
		if timeout:
			return None
		return b
			
	# Returns a bytearray of length `count` read from the serial connection and a boolean value saying whether or not the read timed out
	def readBytes(self, count): # Default to 5 seconds of waiting before timing out
		if self.debug:
			timeout_timer = threading.Timer(5.0, timeoutTimer, (self,))
			self.read_timeout = False
			timeout_timer.start()
			a = bytearray()
			while len(a) < count and not self.read_timeout:
				self.rx_buffer_lock.acquire() # yeah, i could optimize this, but nah
				if len(self.rx_buffer) > 0:
					a.append(self.rx_buffer.pop(0))
				self.rx_buffer_lock.release()
			if not self.read_timeout:
				timeout_timer.cancel()
			return a, self.read_timeout
		else:
			b = self.serial_connection.read(count)
			if len(b) < count: # Reading the bytes from the serial connection timed out
				return None, True
	
	# Returns a signed (positive or negative) integer read from the serial connection
	def readSignedInteger(self, size=INTEGER_SIZE):
		b, timeout = self.readBytes(size)
		if timeout:
			return None
		return int.from_bytes(b, byteorder="big", signed=True)
	
	# Returns a signed (positive only) integer read from the serial connection
	def readUnsignedInteger(self, size=INTEGER_SIZE):
		b, timeout = self.readBytes(size)
		if timeout:
			return None
		return int.from_bytes(b, byteorder="big", signed=False)
	
	# Returns a signed (positive or negative) integer read from the serial connection
	def readInteger(self, size=INTEGER_SIZE):
		b, timeout = self.readBytes(size)
		if timeout:
			return None
		return int.from_bytes(b, byteorder="big", signed=True)
		
	# Returns a float read from the serial connection that was represented in our special ASCII encoded format
	def read_float(self):
		b, timeout = bytearray(self.readBytes(7))
		if timeout:
			return None
		s = b.decode("ascii")
		l = int(s[1:4])
		r = int(s[4:7])
		f = float(l) + (0.001 * float(r))
		if s[0] == '-':
			f = f * -1.0
		return f
		
	# Transmits a file through serial, using error correction and packetization
	def sendFile(self, f, filename):
		if self.sending_file:
			print("ERROR] Cannot send mutliple files at once!")
			return False

		self.sending_file = True
		print("Sending file: " + filename)
		
		filesize = os.stat(f.name).st_size
		packetsize = 1024 #TODO: Make an algorithm to select something that is not hardcoded
		retry_count = 0
		f.seek(0,0)
		#TODO: Finish this
		h = hashlib.new("md5")
		
		d = f.read(512) # 512 is the block size of md5, see: https://stackoverflow.com/questions/42819622/getting-hash-digest-of-a-file-in-python-reading-whole-file-at-once-vs-readin	
		while d:
			h.update(d)
			d = f.read(512)
		file_hash = h.digest() # gives us a bytes object representing the md5 digest
		print("MD5 128bit-digest is: " + str(h.hexdigest()))
		
		while retry_count < 5: # We will only resend the start packet 5 times before giving up on transmission
			self.sendBytes(b'\x12') # magic command code
			self.sendString(filename + ";") # filename terminated by semicolon
			self.sendBytes(filesize.to_bytes(4, byteorder="big", signed=False)) # send file size
			self.sendBytes(packetsize.to_bytes(2, byteorder="big", signed=False)) # send the number of bytes that will be contained in each packet
			self.sendBytes(file_hash) # send the 16 bytes of the md5 digest
			self.sendBytes(retry_count.to_bytes(1, byteorder="big", signed=False)) # send the number of times that we have tried to send the start packet
			
			d = self.readByte()
			if d == b'\x1a':
				reply_ok = True
				check_filename = ''
				while True:
					d = self.readByte()
					if d.decode('ascii') == ";": #possible bug if we never receive a ; character
						break
					else:
						check_filename += d.decode('ascii')
				if not check_filename == filename:
					reply_ok = False
				check_size = self.readUnsignedInteger()
				if not filesize == check_size:
					reply_ok = False
				check_p_size = self.readUnsignedInteger(size=2)
				if not check_p_size == packetsize:
					reply_ok = False
				check_digest, tout = self.readBytes(16)
				if not check_digest == file_hash:
					reply_ok = False
				a = self.readByte()
				if not a == b'\x2a':
					reply_ok = False
					
				if reply_ok:
					break
			
			retry_count += 1
			
		if retry_count >= 5:
			print("ERROR] File transmission failed! Too many retries for start packet. Check to make sure the Rover is listening and connected.")
			self.sending_file = False
			return False
		else:
			print("Received SACK, beginning data transfer...")
			
		self.sending_file = False
			
	def receiveFile(self,fname="None"):
		if self.sending_file or self.receiving_file:
			print("ERROR] Unable to receive multiple files or receive while sending!")
			return False
		
		self.receiving_file = True
		print("Waiting for start packet...")
		
		self.opened_file = False
		done = False
		rx_filename = ''
		file_size = 0
		packet_size = 0
		while not done:
			while self.in_waiting() == 0:
				b=b'' # do nothing while we wait for bytes to come in
		
			b = self.readByte()
		
			if b == b'\x12':
				print("Start...")
				rx_filename = ''
				while True:
					d = self.readByte()
					if d.decode('ascii') == ";":
						break
					else:
						rx_filename += d.decode('ascii')
				print("rx_filename is: " + rx_filename)
				file_size = self.readUnsignedInteger(size=4)
				packet_size = self.readUnsignedInteger(size=2)
				hash, timeout = self.readBytes(16)
				if timeout:
					print("Timed out while reading the MD5 digest for the file!")
					self.receiving_file = False
					return False
				retry_number = self.readByte()
				
				# Send SACK
				self.sendBytes(b'\x1A')
				self.sendString(rx_filename + ";")
				self.sendUnsignedInteger(file_size)
				self.sendBytes(packet_size.to_bytes(2, byteorder="big", signed=False))
				self.sendBytes(hash)
				self.sendBytes(b'\x2A')
				print("Sent SACK")
				
			elif b == b'\x55': # data packet
				if not opened_file:
					if fname == None:
						fname = rx_filename
					f = open("rx_" + fname, "wb")	
					opened_file = True
				retry_number = self.readByte()
				packet_number = self.readUnsignedInteger(size=2)
				fec, timeout = self.readBytes(4)
				if timeout:
					print("Timed out while reading the CRC-32 hash for the packet!")
					fec_ok = False #TODO: This actually doesn't do anything because we already make the comparison below
				
				data = self.readBytes(packet_size)
				calculated_fec = zlib.crc32(data)
				
				fec_ok = fec == calculated_fec
				if fec_ok:
					self.sendBytes(b'\x60')
				else:
					self.sendBytes(b'\x77')
				self.sendBytes(packet_number.to_bytes(2, byteorder="big", signed=False))
				self.sendBytes(calculated_fec)
				
				if fec_ok:
					f.seek(packet_size * packet_number)
					f.write(data)
					f.flush()
			
		self.receiving_file = False

	"""
	When debug_mode is set to True, the program will attempt to connect to the UDP port provided by fake_serial.py.
	debug_rx_port will be the UDP port that we will listen to for incoming connections
	debug_tx_port will be the UDP port that we will connect to when sending bytes
	"""
	def __init__(self, serial_device, baud_rate=9600, debug_mode=False, debug_rx_port=0, debug_tx_port=0, rx_print_prefix=None):
		self.debug = debug_mode
		self.read_timeout = False
		self.rx_print_prefix = rx_print_prefix
		
		# Variables for sending files
		self.sending_file = False
		self.reply_received_condition = threading.Condition()
		self.reply_ok = False # set to True when we receive ACK, set to false for NACK
		
		# Variables for receiving files
		self.receiving_file = False
		self.got_start = False
		self.data_received_condition = threading.Condition()
		
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
			self.serial_connection = serial.Serial(serial_device, baudrate=baud_rate, timeout=5)
			print("Created serial connection to " + serial_device)

	def __del__(self):
		if self.debug:
			self.rx_serv.shutdown()
		else:
			self.serial_connection.close()
