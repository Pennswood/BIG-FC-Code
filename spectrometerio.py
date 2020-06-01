import seabreeze
from seabreeze.spectrometers import Spectrometer as Spec
from file_manager import FileManager
import subprocess
import time

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
	Task: Starting integrating for x milliseconds
	Input: int integration time in milliseconds
	Returns: none
	"""
	def sample(self, milliseconds):
		self.spec.trigger_mode = 0																# Setting the trigger mode to normal
		self.spec.integration_time_micros(milliseconds*1000)									# Set integration time for spectrometer
		self.states_spectrometer = 1															# Spectrometer state is set to sampling
		self.oasis_serial.sendBytes(b'\x30')													# Sending nominal responce
		try:
			wavelengths, intensities = self.spec.spectrum()										# This will return wavelengths and intensities as a 2D array, this call also begins the sampling
		except:
			return 'An error occurred while attempting to sample'								# Command to sample didn't work properly

		data = wavelengths, intensities															# Saving 2D array to variable data
		if data == []:
			return 'No data entered'															# Error handling for no data collected
		self.oasis_serial.sendBytes(b'\x31')													# Code sent to spectrometer signaling sampling has successfully finished
		
		date = time.asctime().replace(" ", "_").replace(":", "_")								# [Fixed] Obtaining date/time through time library
		filename = '{}'.format(date.stdout.decode('utf-8'))										# Creates the time stamped spectrometer file name
		seconds = time.time()																	# Returns # of seconds since Jan 1, 1970 (since epoch)
		# self.fm.save_sample([insert timestamp], data)					# No longer using sdcard
		self.fm.create_spectrometer_file(filename + '.bin', data, seconds)						# Function call to create spectrometer file
		self.states_spectrometer = 0															# Spectrometer state is now on standby
		
		self.oasis_serial.sendBytes(b'\x01')													# Send nominal response for successful completion
		return None

	def __init__(self, serial,file_manager):
		# 0 = standby, 1 = integrating, 2 = disconnected
		self.oasis_serial = serial
		self.states_spectrometer = 0
		self.fm = file_manager
		self.spec = self.setup_spec()
