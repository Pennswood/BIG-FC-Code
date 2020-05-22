# The two value below are for debugging purposes only, they mean nothing to the TLC or BBB
ROVER_TX_PORT = 420 # Emulate sending to the Rover on this port
ROVER_RX_PORT = 421 # Emulate receiving from the Rover

TLC_TX_PORT = 320 # Emulate sending to the TLC on this port
TLC_RX_PORT = 321 # Emulate receiving from the TLC on this port

"""
Task: sends a response to the rover.
Input: An OasisSerial object
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
"""
def ping(s):
	print("PONG")
	s.sendBytes(b'\x01')

"""
Task: sends all spectrometer data to the rover
Input: An OasisSerial object
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
"""
def all_spectrometer_data(s):
	# TODO
	return

'''
Adds all the statuses into a bytearray
'''
# TODO: add comments for what each sendBytes indicates and what inputs are expected
def add_status(tlc_mode, laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd):
	status_array = bytearray()
	if not tlc_mode:						# storage
		status_array += (b'\x01')			# TLC mode | 1 byte
	else:									# operations
		status_array += (b'\x02')
	if laser_status == 0:
		status_array += (b'\x24')			# Laser status | 1 byte
	elif laser_status == 1:
		status_array += (b'\x00')			# TODO: need to add hex for this
	elif laser_status == 2:
		status_array += (b'\x22')
	elif laser_status == 3:
		status_array += (b'\x00')			# TODO: need to add hex for this
	elif laser_status == 4:
		status_array += (b'\x20')
	elif laser_status == 5:
		status_array += (b'\x23')

	if spec_status == 0:					# Spectrometer status | 1 byte
		status_array += (b'\x01')
	if spec_status == 1:
		status_array += (b'\x02')
	if spec_status == 2:
		status_array += (b'\xFC')

	for f in temp_data:						# Assuming that temp_data is an array
		s = "{:0=+4d}{:0=-3d}".format(int(f),int(abs(abs(f)-abs(int(f)))*1000))		# Temperature data | 56 bytes
		status_array += s.encode("ascii")
	
	for i in efdc:							# Assuming EFDC is an array of bytes
		status_array += i					# Etch foil duty cycle (EFDC) | 3 bytes

	errors = 0								# Error codes | 3 bytes
	for index, error in enumerate(error_codes):		# Convert bits into int to bytes
		errors += error * 2**index			
	b = errors.to_bytes(3, byteorder="big", signed=False)
	status_array += b

	status_array += prev_cmd				# Previous command | 1 byte
	return status_array

"""
Task: sends back a byte list of status data (in accordance to table III in rover commands) to the rover)
Input: An OasisSerial object
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
"""
'''
Sends over the current status of the Oasis (temperature, error codes, laser and spectrometer status)
'''
def status_request(s, status_array):
	for i in status_array:
		s.sendBytes(i)


def status_dump(s):
	# TODO
	return


def manifest_request(s):
	# TODO
	return


def transfer_sample(s):
	# TODO
	return


def clock_sync(s):
	# TODO
	return
