"""
Task: sends a response to the rover.
Input: An OasisSerial object
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
"""
def ping(s):
	print("PONG")
	return s.sendByte(b'\x01')

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
def status_request(s):
	# TODO
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
