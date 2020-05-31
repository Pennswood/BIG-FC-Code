import seabreeze
from seabreeze.spectrometers import Spectrometer
from file_manager import FileManager
import subprocess
import time
import oasis_serial

class Spectrometer():
	'''
	Set up the spectrometer
	Return: a spectrometer object or None if error
	'''
	def setup_spec(self):
		if seabreeze.spectrometers.list_devices():
			self.states_spectrometer = 0
			spec = seabreeze.spectrometers.Spectrometer.from_first_available()
			return spec
		else:
			self.states_spectrometer = 2
			print("ERROR: No spectrometer listed by seabreeze!")
			return None

	"""
	Taking integration time int
	"""
	def sample(self, milliseconds):
		self.spec.trigger_mode = 0																# Setting the trigger mode to normal
		self.spec.integration_time_micros(milliseconds*1000)									# Set integration time for spectrometer
		self.states_spectrometer = 1															# Spectrometer state is set to sampling
		oasis_serial.sendBytes(b'\x01')															# Sending nominal responce
		try:
			wavelengths, intensities = self.spec.spectrum()										# This will return wavelengths and intensities as a 2D array, this call also begins the sampling
		except:
			return 'An error occurred while attempting to sample'								# Command to sample didn't work properly

		data = wavelengths, intensities															# Saving 2D array to variable data
		if data == []:
			return 'No data entered'															# Error handling for no data collected
		oasis_serial.sendBytes(b'\x31')		# Code sent to spectrometer signaling sampling has successfully finished
		
		# TODO: Fix the below line of code... it works, but we should really be using Python's built-in functions and not opening up another shell just to get a formatted date string
		date = subprocess.run(['date', "'+%m_%d_%Y_%H_%M_%S'"], timeout = 5, stdout=subprocess.PIPE)	# Running date command on terminal
		filename = '{}'.format(date.stdout.decode('utf-8'))										# Creates the time stamped spectrometer file name
		seconds = time.time()																	# Returns # of seconds since Jan 1, 1970 (since epoch)
		# self.fm.save_sample([insert timestamp], data)					# No longer using sdcard
		self.sdcard.create_spectrometer_file(filename + '.bin', data, seconds)					# Function call to create spectrometer file
		self.states_spectrometer = 0															# Spectrometer state is now on standby
		return None

	# TODO: avoid duplicating this function in this file
	'''
	Task: gets the command rejected response for spectrometer
	Input: int for laser status, int for spectrometer status, 21X1 boolean array for active errors
	Returns: a byte array for the command rejected response
	'''
	def get_cmd_rejected_response_array(self, laser_status, spec_status, active_errors):
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

		return cmd_rejected_array

	def __init__(self, file_manager):
		# 0 = standby, 1 = integrating, 2 = disconnected
		self.states_spectrometer = 0
		self.fm = file_manager
		self.spec = self.setup_spec()
