import subprocess
import platform

class Rover():

	"""
	Task: sends a response to the rover.
	Input: An OasisSerial object
	Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
	"""
	def ping(self):
		print("INFO: Got PING, sending PONG back")
		self.oasis_serial.sendBytes(b'\x01')



	'''
	Task: sends the command rejected response for roverio
	Input: int for laser status, int for spectrometer status, 21X1 boolean array for active errors
	Returns: None
	'''
	def send_cmd_rejected_response(self, laser_status, spec_status, active_errors, prev_cmd):
		cmd_rejected_array = bytearray()

		if laser_status == 0:
			cmd_rejected_array += (b'\x20')			# Laser status | 1 byte
		elif laser_status==1:
			cmd_rejected_array += (b'\x21')
		elif laser_status == 2:
			cmd_rejected_array += (b'\x22')
		elif laser_status == 3:
			cmd_rejected_array += (b'\x23')
		elif laser_status == 4:
			cmd_rejected_array += (b'\x24')
		elif laser_status == 5:
			cmd_rejected_array += (b'\x25')

		if spec_status == 0:						# Spectrometer status | 1 byte
			cmd_rejected_array += (b'\x01')
		elif spec_status == 1:
			cmd_rejected_array += (b'\x02')
		elif spec_status == 2:
			cmd_rejected_array += (b'\xFC')

		errors = 0									# Error codes | 3 bytes
		for index, error in enumerate(active_errors):		# Convert bits into int to bytes
			errors += error * (2**index)
		b = errors.to_bytes(3, byteorder="big", signed=False)
		cmd_rejected_array += b

		cmd_rejected_array += prev_cmd

		self.oasis_serial.sendBytes(b'\xFF')		# send command rejected
		for i in cmd_rejected_array:
			self.oasis_serial.sendBytes(i)
		# maybe check number of bytes in array for error handling?
		return None

	"""
	Task: sends all spectrometer data to the rover
	Input: 
	Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
	"""
	def all_spectrometer_data(self):
		# # command rejected if laser is not off or spectrometer is integrating
		# if laser_status != 0 or spec_status == 1:
		# 	cmd_rejected_array = self.get_cmd_rejected_response_array(laser_status, spec_status, active_errors)

		# 	self.oasis_serial.sendBytes(b'\xFF')			# tells rover that the cmd is rejected
		# 	for i in cmd_rejected_array:
		# 		self.oasis_serial.sendBytes(i)				# sends cmd rejected response
		# 	return 1
		# # command is successfully executed
		# else:
		self.oasis_serial.sendBytes(b'\x14')			# send nominal response directory_start

		file_list = self.fm.list_all_samples()
		for i in file_list:
			try:
				f = open(i, 'rb')
				if f.readable():
					self.oasis_serial.sendBytes(f.read())
				else:
					print("cannot read file")
				f.close()
			except:
				print("error opening file: " + i)
		return 0

	'''
	Task: Organizes all the status logs into a byte array
	Inputs:
			An integer laser_status
			An integer spec_status
			A float array temp_data
			An int (0-255) array efdc (etch foil duty cycle)
			A boolean array error_codes
			A byte prev_cmd
	Return: A bytearray of status log
	'''
	# TODO: add comments for what each sendBytes indicates and what inputs are expected
	def get_status_array(self, laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd):
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
		elif spec_status == 1:
			status_array += (b'\x02')
		elif spec_status == 2:
			status_array += (b'\xFC')

		for f in temp_data:						# Assuming that temp_data is an array
			s = "{:0=+4d}{:0=-3d}".format(int(f),int(abs(abs(f)-abs(int(f)))*1000))		# Temperature data | 56 bytes
			status_array += s.encode("ascii")

		for i in efdc:							# Assuming EFDC is an array of integers (0-255)
			b = i.to_bytes(1, byteorder="big", signed=False)
			status_array += b					# Etch foil duty cycle (EFDC) | 3 bytes

		errors = 0								# Error codes | 3 bytes
		for index, error in enumerate(error_codes):		# Convert bits into int to bytes
			errors += error * (2**index)
		b = errors.to_bytes(3, byteorder="big", signed=False)
		status_array += b

		status_array += prev_cmd				# Previous command | 1 byte
		return status_array

	"""
	Task: sends back a byte list of status data (in accordance to table III in rover commands) to the rover)
	Inputs: A byte array of status logs
	Returns: integer, 0 for success, other numbers for failure to send data (for debugging purposes)
	"""
	def status_request(self, laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd):
		self.oasis_serial.sendBytes(b'\x10')		# send nominal response status_message
		status_array = self.get_status_array(laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd)
		self.oasis_serial.sendBytes(status_array)
		
		if len(status_array) == 72:				# fix this when the number of thermistors are finalized, currently set to 9
			return 0
		else:
			return 1

	# TODO: add documentation
	def get_error_array(self, laser_status, spec_status, error_codes, prev_cmd):
		status_array = bytearray()

		if laser_status == 0:
			status_array += (b'\x20')  # Laser status | 1 byte
		elif laser_status == 1:
			status_array += (b'\x21')
		elif laser_status == 2:
			status_array += (b'\x22')
		elif laser_status == 3:
			status_array += (b'\x23')
		elif laser_status == 4:
			status_array += (b'\x24')
		elif laser_status == 5:
			status_array += (b'\x25')

		if spec_status == 0:  # Spectrometer status | 1 byte
			status_array += (b'\x01')
		elif spec_status == 1:
			status_array += (b'\x02')
		elif spec_status == 2:
			status_array += (b'\xFC')

		errors = 0  # Error codes | 3 bytes
		for index, error in enumerate(error_codes):  # Convert bits into int to bytes
			errors += error * (2 ** index)
		b = errors.to_bytes(3, byteorder="big", signed=False)
		status_array += b

		status_array += prev_cmd  # Previous command | 1 byte
		return status_array

	# TODO: Add documentation
	def error_response(self, laser_status, spec_status, error_codes, cmd):
		self.oasis_serial.sendBytes(b'\xFF') # send error response
		error_array = self.get_status_array(laser_status, spec_status,  error_codes, cmd)
		self.oasis_serial.sendBytes(error_array)
		return error_array

	'''
	Task: dumps all the status file information to the rover
	Inputs: 
	Returns: 0 for successful completion, 1 for error
	'''
	def status_dump(self):
		file_list = self.fm.list_all_logs()
		for i in file_list:
			try:
				f = open(i, 'rb')
				if f.readable():
					self.oasis_serial.sendBytes(f.read())
				else:
					print("cannot read file")
				f.close()
			except:
				print("error opening file: " + i)
		return 0


	def manifest_request(self):
		self.oasis_serial.sendBytes(b'\x12')		# send nominal response file_start
		
		# TODO
		return

	'''
	Task: Sends over the two most recent spectrometer data files
	Input: 
	Returns: 0 for successful completion, 1 for error
	'''
	def transfer_sample(self):
		self.oasis_serial.sendBytes(b'\x12')			# send nominal response file_start
		
		recent_two = self.fm.get_last_two_samples()   	# Saves last 2 spectrometer files to recent_two
		for i in recent_two:                            # Iterating through both files
			if i == "":
				continue                                # Incase of empty string with no file, skip it
			f = open(i, 'r')                            # Open each file in read
			self.oasis_serial.sendString(f.read())      # Sending string over to rover
			f.close()                                   # Close each file when done
		return 0


	def clock_sync(self):
		t = self.oasis_serial.readSignedInteger()
		if t == None:
			print("WARNING: Reading timestamp from Rover timed out!")
			return False

		print("INFO: Got time stamp from CLOCK_SYNC: " + str(t))
		if not platform.system() == "Linux":
			print("WARNING: Not running actual command because not on Linux system...")
			return True
		else:
			try:
				subprocess.run(["date", "+%s", "-s", "@"+str(t)], check=True, timeout=5)
				print("INFO: Set system time to: " + str(t))

				self.oasis_serial.sendBytes(b'\x01')
				return True
			except:
				print("ERROR: The set time command failed!")
				return False


	def __init__(self, oasis_serial, filemanager):
		self.oasis_serial = oasis_serial
		self.fm = filemanager
