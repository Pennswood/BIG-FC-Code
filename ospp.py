"""
Oasis Serial Packet Protocol
Handles sending packets to and from the Rover.
"""
import zlib
import threading
import random
from oasis_config import RETRANSMIT_TIME, INTEGER_SIZE, ACK_PACKET_CODE, OSPP_PREAMBLE, DEBUG_MODE

class ACKPacket():
	"""Represents an ACK packet used to acknowledge that a DATA packet has been received."""

	def to_bytes(self):
		"""Returns the ACK packet as a bytes object for transmission down the serial line."""
		b = OSPP_PREAMBLE
		b += ACK_PACKET_CODE
		b += self.magic_number.to_bytes(1, byteorder="big", signed=False)
		b += zlib.crc32(b).to_bytes(4, byteorder="big", signed=False)
		return b

	def __str__(self):
		"""Returns a string representation of the ACK packet. Used for debugging."""
		return "ACK" + str(self.to_bytes())

	def __init__(self, magic_number):
		self.magic_number = magic_number

class DataPacket():
	"""Represents a DATA packet to be sent or that has been received."""

	def to_bytes(self, magic_number):
		"""Returns the data packet as a bytes object for sending down the serial line"""
		d = OSPP_PREAMBLE
		d += self.code
		d += magic_number.to_bytes(1, byteorder="big", signed=False)
		d += len(self.data).to_bytes(2, byteorder="big", signed=False)
		d += self.data
		d += zlib.crc32(d).to_bytes(4, byteorder="big", signed=False)
		return d
		
	def __str__(self):
		"""Returns a string representation of the DATA packet. Used for debugging."""
		return "DATA " + str(self.code) + " Len: " + str(len(self.data))

	def acknowledge(self):
		self._acknowledged = True
		self._time_up = False

	def pack_bytes(self, b):
		self.data += b

	def pack_float(self, f):
		s = "{:0=+4d}{:0=-3d}".format(int(f), int(abs(abs(f)-abs(int(f)))*1000))
		self.data += s.encode('ascii')

	def pack_string(self, s):
		self.data += s.encode('ascii')

	def pack_integer(self, i, size=INTEGER_SIZE):
		"""Packs a signed (positive or negative), big endian integer into the data array"""
		self.data +=  i.to_bytes(size, byteorder="big", signed=True)

	def pack_signed_integer(self, i, size=INTEGER_SIZE):
		"""Packs a signed (positive or negative), big endian integer into the data array"""
		self.data +=  i.to_bytes(size, byteorder="big", signed=True)

	def pack_unsigned_integer(self, i, size=INTEGER_SIZE):
		"""Packs an unsigned (positive only), big endian integer into the data array"""
		self.data +=  i.to_bytes(size, byteorder="big", signed=False)

	def seek(self, position):
		self._seek_index = position

	def unpack_bytes(self, count):
		d = self.data[self._seek_index:self._seek_index+count]
		self._seek_index += count
		return d

	def unpack_signed_integer(self, size=INTEGER_SIZE):
		d = self.data[self._seek_index:self._seek_index+size]
		self._seek_index += size
		return int.from_bytes(d, byteorder="big", signed=True)

	def unpack_unsigned_integer(self, size=INTEGER_SIZE):
		d = self.data[self._seek_index:self._seek_index+size]
		self._seek_index += size
		return int.from_bytes(d, byteorder="big", signed=False)

	def unpack_float(self):
		b = self.data[self._seek_index:self._seek_index+7]
		self._seek_index += 7
		s = b.decode("ascii")
		left_side = int(s[1:4])
		right_side = int(s[4:7])
		f = float(left_side) + (0.001 * float(right_side))
		if s[0] == '-':
			f = f * -1.0
		return f

	@staticmethod
	def _retransmit_timer(p):
		p._time_up = True

	def __init__(self, code, data=b''):
		self.code = code
		self.data = data
		self._acknowledged = False
		self._transmission_count = 0
		self._seek_index = 0

class PacketManager():
	"""Manages sending and receiving packets from the Rover."""

	def pop(self):
		"""Pops the latest data packet from the RX buffer and returns it."""
		if len(_rx_buffer) != 0:
			return self._rx_buffer.pop()

	def append(self, packet):
		"""Pushes the given packet onto the TX buffer."""
		self._tx_buffer.append(packet)
		
	@staticmethod
	def _read_preamble(serial):
		"""Helper function that reads the 3 bytes preamble on OSPP packets. Returns True if preamble has been read successfully. False otherwise."""
		for b in OSPP_PREAMBLE:
			a, t = serial.read_bytes(1)
			if t or a != b.to_bytes(1, byteorder="big", signed=False):
				if DEBUG_MODE:
					print("Failed to read preamble.")
				return False
		return True
		
	@staticmethod
	def _rx_loop(pm):
		"""Internal thread that manages incoming bytes"""
		while pm.running:
			while pm.running and pm.serial_connection.in_waiting() == 0:
				a = b'' # do nothing while there are no incoming bytes
			
			if not pm.running:
				break
			
			if not PacketManager._read_preamble(pm.serial_connection): # Don't start reading packets until we successfully read the preamble.
				continue # Failed to read preamble, drop those three bytes and attempt to read next three bytes
			
			calc_crc = zlib.crc32(OSPP_PREAMBLE)
			packet_type, t = pm.serial_connection.read_bytes(1)
			calc_crc = zlib.crc32(packet_type, calc_crc)
			magic_num, t = pm.serial_connection.read_bytes(1)
			if t:
				if DEBUG_MODE:
						print("Timedout while reading magic number. Packet is a runt.")
				continue
			calc_crc = zlib.crc32(magic_num, calc_crc)
			magic_num = int.from_bytes(magic_num, byteorder="big", signed=False)
			
			if packet_type == ACK_PACKET_CODE:
				rx_crc, t = pm.serial_connection.read_bytes(4)
				if t:
					continue

				rx_crc = int.from_bytes(rx_crc, byteorder="big", signed=False)
				if calc_crc != rx_crc: # Calculated and received CRC-32 values do not match
					if DEBUG_MODE:
						print("Received ACK with bad CRC-32")
					continue
				
				if magic_num == pm._current_magic_number: # ACK is correct, if it matches with the top packet, acknowledge it
					pm._tx_buffer[0].acknowledge()
				
			else:
				data_size, t = pm.serial_connection.read_bytes(2)
				if t:
					if DEBUG_MODE:
						print("Timedout while reading data size. Packet is a runt.")
					if pm._last_rx_magic != -1:
						last_ack_packet = ACKPacket(pm._last_rx_magic)
						pm._ack_buffer.append(last_ack_packet)
					continue

				calc_crc = zlib.crc32(data_size, calc_crc)
				data_size = int.from_bytes(data_size, byteorder="big", signed=False)
				if DEBUG_MODE:
					print("DATA length is: " + str(data_size))

				data, t = pm.serial_connection.read_bytes(data_size)
				if t:
					if DEBUG_MODE:
						print("Timedout while reading data field. Packet is a runt.")
					if pm._last_rx_magic != -1:
						last_ack_packet = ACKPacket(pm._last_rx_magic)
						pm._ack_buffer.append(last_ack_packet)
					continue
				calc_crc = zlib.crc32(data, calc_crc)

				rx_crc, t = pm.serial_connection.read_bytes(4)
				if t:
					if DEBUG_MODE:
						print("Timedout while reading CRC-32. Packet is a runt.")
					if pm._last_rx_magic != -1:
						last_ack_packet = ACKPacket(pm._last_rx_magic)
						pm._ack_buffer.append(last_ack_packet)
					continue

				rx_crc = int.from_bytes(rx_crc, byteorder="big", signed=False)
				if calc_crc != rx_crc: # Calculated and received CRC-32 values do not match
					if DEBUG_MODE:
						print("Received DATA with bad CRC-32")
					if pm._last_rx_magic != -1:
						last_ack_packet = ACKPacket(pm._last_rx_magic)
						pm._ack_buffer.append(last_ack_packet)
					continue

				ack_packet = ACKPacket(magic_num)
				
				packet_type = int.from_bytes(packet_type, byteorder="big", signed=False)
				if pm._last_rx_magic == magic_num and pm._last_rx_packet.code == packet_type and pm._last_rx_packet.data == data:
					if DEBUG_MODE:
						print("Dropping DATA packet because magic is the same and is a repeat")
					if pm._last_rx_magic != -1:
						last_ack_packet = ACKPacket(pm._last_rx_magic)
						pm._ack_buffer.append(last_ack_packet)
					continue
				
				if magic_num == pm._last_rx_magic:
					print("WARNING: Got two different packets with the same magic numbers!")
				
				pm._ack_buffer.append(ack_packet)

				data_packet = DataPacket(packet_type, data)
				pm._last_rx_packet = data_packet
				pm._last_rx_magic = magic_num
				pm._rx_buffer.append(data_packet)

	@staticmethod
	def _tx_loop(pm):
		"""Internal thread that manages outgoing packets"""
		while pm.running:
			while len(pm._ack_buffer) != 0: # Send all ACKs that are waiting to be sent
				a = pm._ack_buffer.pop()
				pm.serial_connection.send_bytes(a.to_bytes())
				if DEBUG_MODE:
					print("INFO] Sent ACK " + str(a.magic_number))
		
			if len(pm._tx_buffer) != 0:

				if pm._tx_buffer[0]._transmission_count == 0: # Topmost packet has not been sent yet, send it and start counting down to retransmission
					a = pm._current_magic_number
					while a == pm._current_magic_number: # Select a new magic number that is not a repeat
						a = random.randint(0,255)
					pm._current_magic_number = a
					pm.serial_connection.send_bytes(pm._tx_buffer[0].to_bytes(pm._current_magic_number))
					pm._tx_buffer[0]._transmission_count += 1
					pm._tx_buffer[0]._time_up = False # This will be set to true once the retransmission timer finishes
					pm._tx_buffer[0]._timer = threading.Timer(RETRANSMIT_TIME, DataPacket._retransmit_timer, args=(pm._tx_buffer[0],))
					pm._tx_buffer[0]._timer.start() # Start counting down the retransmission timer
					if DEBUG_MODE:
						print("INFO] TX'd DATA packet " + str(pm._current_magic_number))

				elif pm._tx_buffer[0]._acknowledged: # We got an ACK for the packet, remove it from the buffer and move on to the next packet
					pm._tx_buffer.pop()

				elif pm._tx_buffer[0]._time_up: # retransmission timer has counted down, time to retransmit the packet
					pm.serial_connection.send_bytes(pm._tx_buffer[0].to_bytes(pm._current_magic_number))
					pm._tx_buffer[0]._transmission_count += 1
					pm._tx_buffer[0]._time_up = False
					pm._tx_buffer[0]._timer = threading.Timer(RETRANSMIT_TIME, DataPacket._retransmit_timer, args=(pm._tx_buffer[0],))
					pm._tx_buffer[0]._timer.start()
					
					if DEBUG_MODE:
						print("INFO] Re-TX'd DATA packet " + str(pm._current_magic_number) + " retry # " + str(pm._tx_buffer[0]._transmission_count))

	def __init__(self, serial_connection):
		self.serial_connection = serial_connection
		self._tx_buffer = []
		self._rx_buffer = []
		self._last_rx_packet = None
		self._last_rx_magic = -1
		self._current_magic_number = random.randint(0,255)
		self._ack_buffer = []
		self.running = True
		self._rx_thread = threading.Thread(target=PacketManager._rx_loop, args=(self,))
		self._tx_thread = threading.Thread(target=PacketManager._tx_loop, args=(self,))
		self._rx_thread.start()
		self._tx_thread.start()
