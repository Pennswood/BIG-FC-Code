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
	
"""
Task: sends back a byte list of status data (in accordance to table III in rover commands) to the rover)
Input: An OasisSerial object
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
"""
'''
Sends over the current status of the Oasis (temperature, error codes, laser and spectrometer status)
'''
# TODO: add comments for what each sendBytes indicates and what inputs are expected
def status_request(s, tlc_mode, laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd):
	print("Got status request...")
	if not tlc_mode:					# storage
		s.sendBytes(b'\x01')			# TLC mode | 1 byte
	else:								# operations
		s.sendBytes(b'\x02')
	if laser_status == 0:
		s.sendBytes(b'\x24')			# Laser status | 1 byte
	elif laser_status == 1:
		s.sendBytes('\x00')				# TODO: need to add hex for this
	elif laser_status == 2:
		s.sendBytes(b'\x22')
	elif laser_status == 3:
		s.sendBytes(b'\x00')			# TODO: need to add hex for this
	elif laser_status == 4:
		s.sendBytes(b'\x20')
	elif laser_status == 5:
		s.sendBytes(b'\x23')

	if spec_status == 0:				# Spectrometer status | 1 byte
		s.sendBytes(b'\x01')
	if spec_status == 1:
		s.sendBytes(b'\x02')
	if spec_status == 2:
		s.sendBytes(b'\xFC')

	for i in temp_data:					# Assuming that temp_data is an array
		s.sendFloat(i)					# Temperature data | 56 bytes
	
	for i in etch_foil_duty_cycle:		# Assuming EFDC is an array of bytes
		s.sendBytes(i)					# Etch foil duty cycle (EFDC) | 3 bytes

	errors = [0, 0, 0]					# Error codes | 3 bytes
	for index, error in enumerate(error_codes):		# Convert bits into int to bytes
		if (index//8 == 0):				# First 8 bits in first byte
			errors[0] += error * 2**(index%8)
		elif (index//8 == 1):			# Second 8 bits in second byte
			errors[1] += error * 2**(index%8)
		else:							# Third 5 bits in third byte with 3 bits of zeroes padding
			errors[2] += error * 2**(index%8)
	for i in errors:					# loop through the 3 bytes
		s.sendInt(i)

	s.sendBytes(prev_cmd)				# Previous command | 1 byte
	return


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
