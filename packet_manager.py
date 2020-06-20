"""
Handles sending packets to and from the Rover.
"""
import zlib
import threading
from oasis_config import RETRANSMIT_TIME, INTEGER_SIZE, ACK_PACKET_CODE

class ACKPacket():
	"""Represents an ACK packet used to acknowledge that a DATA packet has been received."""

	def to_bytes(self):
		"""Returns the ACK packet as a bytes object for transmission down the serial line."""
		b = ACK_PACKET_CODE
		b += self.sequence_number.to_bytes(1, byteorder="big", signed=False)
		b += zlib.crc32(b).to_bytes(4, byteorder="big", signed=False)
		return b

	def __init__(self, sequence_number):
		self.sequence_number = sequence_number

class DataPacket():
	"""Represents a DATA packet to be sent or that has been received."""

	def to_bytes(self, sequence_number):
		"""Returns the data packet as a bytes object for sending down the serial line"""
		d = b''
		d += self.code
		d += sequence_number.to_bytes(1, byteorder="big", signed=False)
		d += len(self.data).to_bytes(2, byteorder="big", signed=False)
		d += data
		d += zlib.crc32(d).to_bytes(4, byteorder="big", signed=False)
		return d

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
		self._transmission_count = 0'
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
	def _rx_loop(pm):
		"""Internal thread that manages incoming bytes"""
		while pm.running:
			while pm.serial_connection.in_waiting() == 0:
				a = b'' # do nothing while there are no incoming bytes
			
			
			packet_type = pm.serial_connection.readByte()
			calc_crc = zlib.crc32(packet_type)
			seq_num, t = pm.serial_connection.read_bytes(1)
				if t:
					continue
			calc_crc = zlib.crc32(seq_num, calc_crc)
			
			if packet_type == ACK_PACKET_CODE:
				rx_crc, t = pm.serial_connection.read_bytes(4)
				if t:
					continue

				rx_crc = int.from_bytes(crc, byteorder="big", signed=False)
				if calc_crc != rx_crc: # Calculated and received CRC-32 values do not match
					continue
					
				seq_num = int.from_bytes(seq_num, byteorder="big", signed=False)
				
				
				if pm._tx_seq_num == seq_num: # ACK is correct, if it matches with the top packet, acknowledge it
					pm._tx_buffer[0].acknowledge()
				
			else:
				data_size, t = pm.serial_connection.read_bytes(2)
				if t:
					continue
				calc_crc = zlib.crc32(data_size, calc_crc)
				data_size = int.from_bytes(data_size, byteorder="big", signed=False)
				
				data, t = pm.serial_connection.read_bytes(data_size)
				if t:
					continue
				calc_crc = zlib.crc32(data, calc_crc)
				
				rx_crc, t = pm.serial_connection.read_bytes(4)
				if t:
					continue

				rx_crc = int.from_bytes(crc, byteorder="big", signed=False)
				if calc_crc != rx_crc: # Calculated and received CRC-32 values do not match
					continue
				
				ack_packet = ACKPacket(seq_num)
				
				if seq_num < pm._rx_seq_num: # packet is a repeat
					pm._ack_buffer.append(ack_packet)
					continue
				elif seq_num == pm._rx_seq_num: # packet is new
					pm._ack_buffer.append(ack_packet)
					pm._rx_seq_num += 1
					if pm._rx_seq_num >= 255:
						pm._rx_seq_num = 1
					data_packet = DataPacket(packet_type, data)
					pm._rx_buffer.append(data_packet)

	@staticmethod
	def _tx_loop(pm):
		"""Internal thread that manages outgoing packets"""
		while pm.running:
			while len(pm._ack_buffer) != 0: # Send all ACKs that are waiting to be sent
				a = pm._ack_buffer.pop()
				pm.serial_connection.sendBytes(a.to_bytes)
		
			if len(pm._tx_buffer) != 0:
				if pm._tx_buffer[0].transmission_count == 0: # Topmost packet has not been sent yet, send it and start counting down to retransmission
					pm.serial_connection.send_bytes(pm._tx_buffer[0].to_bytes(pm._tx_seq_num))
					pm._tx_buffer[0].transmission_count += 1
					pm._tx_buffer[0]._time_up = False # This will be set to true once the retransmission timer finishes
					pm._tx_buffer[0]._timer = threading.Timer(RETRANSMIT_TIME, DataPacket._retransmit_timer(pm._tx_buffer[0])
					pm._tx_buffer[0]._timer.start() # Start counting down the retransmission timer

				elif pm._tx_buffer[0]._acknowledged: # We got an ACK for the packet, remove it from the buffer and move on to the next packet
					pm._tx_buffer.pop()
					pm._tx_seq_num += 1
					if pm._tx_seq_num >= 255: # seq. number only takes up one byte, so it cannot be greater than 255
						pm._tx_seq_num = 1

				elif pm._tx_buffer[0]._time_up: # retransmission timer has counted down, time to retransmit the packet
					pm.serial_connection.send_bytes(pm._tx_buffer[0].to_bytes(pm._tx_seq_num))
					pm._tx_buffer[0].transmission_count += 1
					pm._tx_buffer[0]._time_up = False
					pm._tx_buffer[0]._timer = threading.Timer(RETRANSMIT_TIME, DataPacket._retransmit_timer(pm._tx_buffer[0])
					pm._tx_buffer[0]._timer.start()

	def __init__(self, serial_connection):
		self.serial = serial_connection
		self._tx_buffer = []
		self._rx_buffer = []
		self._rx_seq_num = 1 # The sequence number of the next data packet we expect to receive
		self._tx_seq_num = 1 # The sequence number of the last data packet we sent
		self._ack_buffer = []
		self.running = True
		self._rx_thread = threading.Thread(target=PacketManager._rx_loop, args=(self,))
		self._tx_thread = threading.Thread(target=PacketManager._tx_loop, args=(self,))
		self._rx_thread.start()
		self._tx_thread.start()


	def __del__(self):
		self.running = False
		self._rx_thread.join()
		self._tx_thread.start()