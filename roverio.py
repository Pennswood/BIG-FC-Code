"""
Manages commands that interact with the Rover.
Such as: pinging, status request, transferring samples.
"""
import subprocess
import platform

class Rover():
	"""
	This class really doesn't represent the Rover at all.
	It's just a neat way to organize a bunch of methods.
	This should really be refactored.
	"""
	def ping(self):
		"""
		Sends a response to the rover.
		
		Parameters
		----------
		oasis_serial : object
			An Oasis Serial object

		Returns
		-------
		successful : boolean
			Returns True for success and False for unsuccessful
		"""
		print("INFO: Got PING, sending PONG back")
		self.oasis_serial.send_bytes(b'\x01')

	def send_cmd_rejected_response(self, laser_status, spec_status, active_errors, prev_cmd):
		"""
		Sends the command rejected response for roverio

		Parameters
		----------
		laser_status : int
			This integer represents the state of the laser

		spec_status : int
			This integer represents the state of the spectrometer
		
		active_errors : list
			A 21x1 boolean array for active errors

		prev_cmd : bytes
			These hold the most recent command send from the rover
		"""
		cmd_rejected_array = bytearray()

		if laser_status == 0:
			cmd_rejected_array += (b'\x20')			# Laser status | 1 byte
		elif laser_status == 1:
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

		self.oasis_serial.send_bytes(b'\xFF')		# send command rejected
		for i in cmd_rejected_array:
			self.oasis_serial.send_bytes(i)
		# maybe check number of bytes in array for error handling?

	def all_spectrometer_data(self):
		"""
		Sends all spectrometer data to the rover

		Returns
		-------
		success : int
			This will return 0 for success, otherwise this will return other numbers for failure to open file (for debugging purposes)
		"""
		self.oasis_serial.send_bytes(b'\x14')			# send nominal response directory_start
		self.oasis_serial.send_string("samples/;")		# send directory name

		debug_int = 0									# return 1 if error for debugging purposes
		file_list = self.fm.list_all_samples()
		for i in file_list:
			try:
				f = open(i, 'rb')
				if f.readable():
					self.oasis_serial.send_file(f, i)
				else:
					print("ERROR: Unable to read file" + i)
				f.close()
			except:
				print("ERROR: Unable to open file: " + i)
				debug_int = 1
		return debug_int


	# TODO: add comments for what each sendBytes indicates and what inputs are expected
	def get_status_array(self, laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd):
		"""
		Organizes all the status logs into a byte array

		Parameters
		----------
		laser_status : int
			This integer represents the state of the laser
		
		spec_status : int
			This integer represents the state of the spectrometer

		temp_data : list
			A float array of tempurature data

		duty_cycle : list
			An int (0-255) array efdc (etch foil duty cycle)

		error_codes : list
			A boolean array containing error codes
		
		prev_cmd : bytes
			A byte representing the last command send from rover

		Return
		------
		byte_array : list
			A byte array of status log
		"""
		status_array = bytearray()

		# Laser status | 1 byte
		if laser_status == 0:
			status_array += (b'\x20')
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

		# Spectrometer status | 1 byte
		if spec_status == 0:
			status_array += (b'\x01')
		elif spec_status == 1:
			status_array += (b'\x02')
		elif spec_status == 2:
			status_array += (b'\xFC')

		for f in temp_data: # Assuming that temp_data is an array
			# Encode each float into a standard sized ASCII string
			s = "{:0=+4d}{:0=-3d}".format(int(f), int(abs(abs(f)-abs(int(f)))*1000))
			status_array += s.encode("ascii")

		for i in efdc: # Assuming EFDC is an array of integers (0-255)
			b = i.to_bytes(1, byteorder="big", signed=False)
			status_array += b # Etch foil duty cycle (EFDC) | 3 bytes

		errors = 0 # Error codes | 3 bytes
		for index, error in enumerate(error_codes): # Convert bits into int to bytes
			errors += error * (2**index)
		b = errors.to_bytes(3, byteorder="big", signed=False)
		status_array += b

		status_array += prev_cmd # Previous command | 1 byte
		return status_array


	def status_request(self, laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd):
		"""
		Sends back a byte list of status data (in accordance to table III in rover commands)
		
		Parameters
		----------
		byte_array : list
			A byte array of status logs
		
		Returns
		-------
		success : int
			integer, 0 for success, other numbers for failure to send data
		"""
		self.oasis_serial.send_bytes(b'\x10') # send nominal response status_message
		status_array = self.get_status_array(laser_status, spec_status, temp_data, efdc, error_codes, prev_cmd)
		self.oasis_serial.send_bytes(status_array)

		# TODO: Why does this if statement exist?
		if len(status_array) == 72:
			return 0

		return 1

	def status_dump(self):
		"""
		Dumps all the status file information to the rover
		"""
		self.oasis_serial.send_bytes(b'\x14') # send nominal response directory_start
		self.oasis_serial.send_string("logs/;") # send directory name

		file_list = self.fm.list_all_logs()
		for i in file_list:
			try:
				f = open(i, 'rb')
				if f.readable():
					self.oasis_serial.send_file(f, i)
				else:
					print("ERROR: Unable to read file" + i)
				f.close()
			except:
				print("ERROR: Unable to open file: " + i)

	def transfer_sample(self):
		"""
		Sends the two most recent spectrometer sample files.

		Returns
		-------
		success : int
			0 for successful completion, 1 for error
		"""
		recent_two = self.fm.get_last_two_samples() # Saves last 2 spectrometer files to recent_two
		for i in recent_two: # Iterating through both files
			if i is None:
				continue # Incase of empty string with no file, skip it
			try:
				f = open(i, 'rb')
				if f.readable():
					self.oasis_serial.send_file(f, i)
				else:
					print("ERROR: Unable to read file" + i)
				f.close()
			except:
				print("ERROR: Unable to open file: " + i)
		return 0


	def clock_sync(self):
		"""
		Called when the CLOCK SYNC command code is received. Sets the system clock to the received UNIX timestamp.
		"""
		t = self.oasis_serial.read_signed_integer()
		if t is None:
			print("WARNING: Reading timestamp from Rover timed out!")
			return False

		print("INFO: Got time stamp from CLOCK_SYNC: " + str(t))
		if not platform.system() == "Linux":
			print("WARNING: Not running actual command because not on Linux system...")
			return True

		try:
			subprocess.run(["date", "+%s", "-s", "@"+str(t)], check=True, timeout=5)
			print("INFO: Set system time to: " + str(t))

			self.oasis_serial.send_bytes(b'\x01')
			return True
		except:
			print("ERROR: The set time command failed!")
			return False


	def __init__(self, oasis_serial, filemanager):
		self.oasis_serial = oasis_serial
		self.fm = filemanager
