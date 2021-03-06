"""
Module for connecting to either physical serial lines or "virtual" serial lines (UDP sockets) for debugging.
Handles low level reading of integers, strings, floats, files.
"""
import socket
import os
import zlib
import hashlib
import threading
import socketserver
import serial

from oasis_config import DEBUG_MODE, DEBUG_BUFFER_SIZE, INTEGER_SIZE

# Unless Tyler tells you to, DONT touch this file. If you are getting errors in your code its probably because your code is wrong :) If you really think it's this code, message me

def _debug_udp_handler_factory(oserial):
	"""Class factory for DebugUDPHandler so that we can pass in an OasisSerial object to the object."""

	class DebugUDPHandler(socketserver.BaseRequestHandler):
		"""Callback for when the UDP socket server receives data"""

		def setup(self):
			"""Called after initialization, this is where we make sure the object has access to
			an OasisSerial object, so that it can fill its rx_buffer."""
			self.oasis_serial = oserial

		def handle(self):
			"""We got data from our socket, fill the rx buffer."""
			self.data = self.request[0]

			self.oasis_serial.rx_buffer_lock.acquire()
			if self.oasis_serial.rx_print_prefix:
				print(self.oasis_serial.rx_print_prefix + str(self.data))
			self.oasis_serial.rx_buffer += self.data
			self.oasis_serial.rx_buffer_lock.release()
	return DebugUDPHandler

def _debug_udp_timeout_timer(oserial):
	"""Callback for when reading bytes from debug serial input timeouts"""
	print("Timeout")
	oserial.read_timeout = True

class OasisSerial():
	"""Class that represents a serial connection.
	Passing debug_mode=True will cause this to open up a UDP
	server to receive debug serial data, and will write all
	serial data to a UDP port as well"""

	def in_waiting(self):
		"""
		Return the number of characters currently in the input buffer
		
		Returns
		-------
		int
			Number of characters in input buffer
		"""
		if self.debug:
			self.rx_buffer_lock.acquire()
			count = len(self.rx_buffer)
			self.rx_buffer_lock.release()
			return count

		return self.serial_connection.in_waiting

	def send_bytes(self, b):
		"""
		Sends bytes over to the dummy rover

		Parameters
		----------
		b : bytes
			Bytes to be sent over to the dummy rover
		"""
		if self.debug:
			self.udp_tx_socket.sendto(b, ("localhost", self.tx_port))
		else:
			self.serial_connection.write(b)

	def read_byte(self):
		"""
		Returns a single byte read from the serial connection. Returns None if timed out reading the byte

		Returns
		-------
		b : bytes
			The byte received from the serial connection
		"""
		b, timeout = self.read_bytes(1)
		if timeout:
			return None
		return b

	def read_bytes(self, count):
		"""
		Returns a bytearray of length `count` read from the serial connection and a boolean value saying whether or not the read timed out

		Parameters
		----------
		count : int
			A float to be sent over to the dummy rover

		Returns
		-------
		a : list
			A byte array of bytes received from the serial connection
		read_timeout : bool
			A boolean representing whether the read timed out or not
		"""
		if self.debug:
			timeout_timer = threading.Timer(5.0, _debug_udp_timeout_timer, (self,)) # Default to 5 seconds of waiting before timing out
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

		b = self.serial_connection.read(count)
		if len(b) < count: # Reading the bytes from the serial connection timed out
			return None, True

	def send_file(self, f, filename):
		"""
		Transmits a file through serial, using error correction and packetization

		Parameters
		----------
		f : object
			A file object based on the filename

		filename : str
			The name of the file being transmitted

		Returns
		-------
		bool
			A boolean representing whether or not the file was sent successfully
		"""
		if self.sending_file:
			print("ERROR] Cannot send mutliple files at once!")
			return False

		self.sending_file = True
		print("Sending file: " + filename)

		file_size = os.stat(f.name).st_size
		packet_size = 512 #TODO: Make an algorithm to select something that is not hardcoded
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
		f.seek(0)

		while retry_count < 5: # We will only resend the start packet 5 times before giving up on transmission
			self.send_bytes(b'\x12') # magic command code
			self.send_string(filename + ";") # filename terminated by semicolon
			self.send_unsigned_integer(file_size, size=4) # send file size
			self.send_unsigned_integer(packet_size, size=2) # send the number of bytes that will be contained in each packet
			self.send_bytes(file_hash) # send the 16 bytes of the md5 digest
			self.send_unsigned_integer(retry_count, size=1) # send the number of times that we have tried to send the start packet

			d = self.read_byte()
			if d == b'\x1a':
				reply_ok = True
				check_filename = ''
				while True:
					d = self.read_byte()
					if d.decode('ascii') == ";": #possible bug if we never receive a ; character
						break

					check_filename += d.decode('ascii')
				if check_filename != filename:
					reply_ok = False
				check_size = self.read_unsigned_integer(size=4)
				if file_size != check_size:
					reply_ok = False
				check_p_size = self.read_unsigned_integer(size=2)
				if check_p_size != packet_size:
					reply_ok = False
				check_digest, tout = self.read_bytes(16)
				if check_digest != file_hash:
					reply_ok = False
				a = self.read_byte()
				if a != b'\x2a':
					reply_ok = False

				if reply_ok:
					break

			retry_count += 1

		if retry_count >= 5:
			print("ERROR] File transmission failed! Too many retries for start packet. Check to make sure the Rover is listening and connected.")
			self.sending_file = False
			return False

		print("Received SACK, beginning data transfer...")
		tx_count = 0 # Number of bytes transmitted
		packet_number = 0
		while tx_count < file_size:

			f.seek(packet_size * packet_number)
			data = f.read(packet_size)

			#Zero pad our data before running it through the CRC32 hash
			diff = packet_size - len(data)
			pad = bytes(diff)
			data += pad

			packet_crc = zlib.crc32(data)

			retry_count = 0
			while retry_count < 10:
				self.send_bytes(b'\x55')
				self.send_unsigned_integer(retry_count, size=1)
				self.send_unsigned_integer(packet_number, size=2)
				self.send_unsigned_integer(packet_crc, size=4)
				self.send_bytes(data)

				d = self.read_byte()
				if d == b'\x60': # ACK
					ack_packet_number = self.read_unsigned_integer(size=2)
					ack_hash = self.read_unsigned_integer(size=4)
					print("Got ACK " + str(ack_packet_number))
					if ack_hash == packet_crc and ack_packet_number == packet_number: # if the ack's crc32 hash matches and the packet number matches, move on to the next packet
						break

					print("INFO: ACK packet's crc32 does not match ours. Resending packet.")
				elif d == b'\x77': # NACK
					nack_packet_number = self.read_unsigned_integer(size=2)
					print("Got NACK " + str(nack_packet_number))
					if nack_packet_number != packet_number:
						print("NACK says packet numbers don't match! Nothing we can really do other than resend data packet...")

				retry_count += 1

			packet_number += 1
			tx_count += packet_size
		print("Done sending file.")
		self.sending_file = False

	def receive_file(self, fname="None"):
		"""
		Prepares to receive a file. Mainly used in dummy_rover.py

		Parameters
		----------
		fname : str
			The name of the file
		"""
		if self.sending_file or self.receiving_file:
			print("ERROR] Unable to receive multiple files or receive while sending!")
			return False

		self.receiving_file = True
		print("Waiting for start packet...")

		rx_filename = ''
		file_size = 0 # size of the file we are sending, in bytes
		packet_size = 0	# size of the data contained in each packet we receive
		packet_number = 0 # the current packet number
		last_packet_number = -1 # the number of the laster received packet, ensures that we are receiving in sequence
		sent_sack = False # keeps track of whether or not we acknowledged the start packet

		b = b'' # Control Byte read

		# First we will loop until we get a start packet
		done = False
		while not done: # TODO: Replace this with a timeout
			while self.inWaiting() == 0:
				b = b'' # do nothing while we wait for bytes to come in

			b = self.read_byte()

			if b == b'\x12':
				print("Got start file control byte...")
				rx_filename = ''
				while True:
					d = self.read_byte()
					if d.decode('ascii') == ";":
						break

					rx_filename += d.decode('ascii')
				print("rx_filename is: " + rx_filename)
				file_size = self.read_unsigned_integer(size=4)
				packet_size = self.read_unsigned_integer(size=2)
				digest, timeout = self.read_bytes(16)
				if timeout:
					print("Timed out while reading the MD5 digest for the file!")
					self.receiving_file = False
					return False
				retry_number = self.read_byte()

				# Send SACK
				self.send_bytes(b'\x1A')
				self.send_string(rx_filename + ";")
				self.send_unsigned_integer(file_size)
				self.send_unsigned_integer(packet_size, size=2)
				self.send_bytes(digest)
				self.send_bytes(b'\x2A')
				sent_sack = True
				print("Sent SACK")
			elif sent_sack and b == b'\x55':
				done = True # Alright, we sent a SACK and they've now started sending DATA packets, so switch over to handle packets
			else:
				print("ERROR: Out of order byte sent while in file receiving mode!? Check your implementation, ignoring...")

		to_read = file_size		#Number of bytes left to read

		if fname == None:
			fname = rx_filename
		f = open("rx_" + fname, "wb")

		while to_read > 0:
			if b == b'\x55': # data packet
				retry_number = self.read_byte()
				packet_number = self.read_unsigned_integer(size=2)

				fec = self.read_unsigned_integer(size=4) # read the crc32 hash they sent for the packet data
				data, tout = self.read_bytes(packet_size)

				number_ok = last_packet_number == packet_number or packet_number == last_packet_number + 1 # Make sure the packet number they sent makes sense, we should be sending sequentially (or resending the current packet number)
				if not number_ok:
					print("WARNING] Got incorrect or out of order packet number! Dropping packet and sending NACK")
				else:
					last_packet_number = packet_number

				if tout:
					print("Failed to read all of packet data without timing out! Sending NACK")

				fec_ok = False
				if not tout: # Only check the crc32 if we received all the data bytes
					calculated_fec = zlib.crc32(data) # calculate the crc32 hash of the received data
					fec_ok = fec == calculated_fec # double check that the received crc32 hash and our calculated one match

				if fec_ok and number_ok and not tout: # crc32 hashes match, packet number makes sense, so send an ACK
					self.send_bytes(b'\x60') # send an ACK
					self.send_unsigned_integer(packet_number, size=2) # send the packet number we are acknowledging
					self.send_unsigned_integer(calculated_fec, size=4) # send them the crc32 hash we calculated to double check that we heard their crc32 hash correctly
					print("Sent ACK " + str(packet_number))
				else:
					self.send_bytes(b'\x77') # send a NACK
					self.send_unsigned_integer(packet_number, size=2) # send the packet number that we want them to resend
					print("Sent NACK " + str(packet_number))

				if fec_ok: # we sent our ACK, so write down the data we received
					f.seek(packet_size * packet_number) # always set to the packet number in case they send up the same packet number again (if we send an ACK with an incorrect crc32 value)
					if to_read < packet_size: # This should be the last packet, and it should be zero padded, so remove the zero padding
						data = data[:to_read]
					to_read -= len(data)
					f.write(data)
					f.flush()
					print("To read: " + str(to_read))
					if to_read <= 0:
						print("File received.")
						f.close()
						break
			else:
				print("WARNING: Got command byte other than 0x55 during file transfer mode! Ignoring...")

			while self.inWaiting() == 0:
				b = b'' # do nothing while we wait for bytes to come in
			b = self.read_byte()

		self.receiving_file = False

	def __init__(self, serial_device, baud_rate=9600, debug_mode=False, debug_rx_port=0, debug_tx_port=0, rx_print_prefix=None):
		# """
		# When debug_mode is set to True, the program will attempt to connect to the UDP port provided by fake_serial.py.
		# debug_rx_port will be the UDP port that we will listen to for incoming connections
		# debug_tx_port will be the UDP port that we will connect to when sending bytes
		# """
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
			self.rx_serv = socketserver.UDPServer(("localhost", debug_rx_port), _debug_udp_handler_factory(self))
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
