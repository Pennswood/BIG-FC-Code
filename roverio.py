import subprocess
import platform

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
Task: Organizes all the status logs into a byte array
Inputs:
		An integer laser_status
		An integer spec_status
		A float array temp_data
		A byte array efdc (etch foil duty cycle)
		A boolean array error_codes
		A byte prev_cmd
Return: A bytearray of status log
'''
# TODO: add comments for what each sendBytes indicates and what inputs are expected
def get_status_array(laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd):
	status_array = bytearray()
	
	if laser_status == 0:
		status_array += (b'\x20')			# Laser status | 1 byte
	elif laser_status==1:
		status_array += (b'\x21')
	elif laser_status == 2:
		status_array += (b'\x22')
	elif laser_status == 3:
		status_array += (b'\x23')
	elif laser_status == 4:
		status_array += (b'\x24')
	elif laser_status == 5:
		status_array += (b'\x25')

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
Inputs: An OasisSerial object, A byte array of status logs
Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
"""
def status_request(s, status_array):
	for i in status_array:
		s.sendBytes(i)
	if len(status_array) == 66:				# fix this when the number of thermistors are finalized
		return 0
	else:
		return 1

'''
Task: dumps all the status file information to the rover
Inputs: An OasisSerial object, An sdcardio object
'''
def status_dump(s, sdcard):
	file_list = sdcard.read_all_log_file()
	for i in file_list:
		try:
			f = open(i, 'rb')
			if f.readable():
				s.sendBytes(f.read())
			f.close()
		except:
			print("error opening file: " + i)
	return


def manifest_request(s):
	# TODO
	return


def transfer_sample(s, sdcard):
    recent_two = sdcard.last_two_spectrometer_file()    # Saves last 2 spectrometer files to recent_two
    for i in recent_two:                                # Iterating through both files
        if i == "":
            continue                                    # Incase of empty string with no file, skip it
        f = open(i, 'r')                                # Open each file in read
        s.sendString(f.read())                          # Sending string over to rover
        f.close()                                       # Close each file when done
    return None


def clock_sync(s):
	print("CLOCK SYNC")
	t = s.readSignedInteger()
	if t == None:
		print("WARNING] Reading timestamp from Rover timed out!")
		return False
		
	print("Got time stamp: " + str(t))
	if not platform.system() == "Linux":
		print("Not running actual command because not on Linux system...")
		return True
	else:
		try:
			subprocess.run(["date", "+%s", "-s", "@"+str(t)], check=True, timeout=5)
			print("Set system time to: " + str(t))
			return True
		except:
			print("ERROR] The set time command failed!")
			return False