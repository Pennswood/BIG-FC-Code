"""
Manages communication with the spectrometer through the SeaBreeze library.
"""
import time

import seabreeze
import seabreeze.spectrometers

class Spectrometer():
	"""Class for interacting with the spectrometer through seabreeze."""

	def _setupSpectrometer(self):
		"""
		Set up method for the spectrometer.
		
		Returns
		-------
		object
			A spectrometer object
		None
			If an error occurs
		"""
		if seabreeze.spectrometers.list_devices():
			self.states_spectrometer = 0
			spec = seabreeze.spectrometers.Spectrometer.from_first_available()
			return spec

		self.states_spectrometer = 2
		print("ERROR: No spectrometer listed by seabreeze!")
		return None

	def sample(self, milliseconds):
		"""
		This function is used to signal the spectrometer to integrate for a set amount of time.

		Parameters
		----------
		milliseconds : int
			Inputted integration time for spectrometer
		
		Returns
		-------
		None
		"""
		self.spec.trigger_mode = 0 # Setting the trigger mode to normal
		self.spec.integration_time_micros(milliseconds*1000) # Set integration time for spectrometer
		self.states_spectrometer = 1 # Spectrometer state is set to sampling
		self.oasis_serial.sendBytes(b'\x01') # Sending nominal responce
		try:
			wavelengths, intensities = self.spec.spectrum() #Returns wavelengths and intensities as a 2D array, and begins sampling
		except:
			return 'An error occurred while attempting to sample' # Command to sample didn't work properly

		data = wavelengths, intensities # Saving 2D array to variable data
		if data == []:
			return 'No data entered' # Error handling for no data collected
		self.oasis_serial.sendBytes(b'\x30') # Code sent to spectrometer signaling sampling has successfully finished

		timestamp = time.time() # Returns # of seconds since Jan 1, 1970 (since epoch)
		self.fm.save_sample(timestamp, data) # Function call to create spectrometer file
		self.states_spectrometer = 0 # Spectrometer state is now on standby

		return None

	def __init__(self, serial, file_manager):
		# 0 = standby, 1 = integrating, 2 = disconnected
		self.oasis_serial = serial
		self.states_spectrometer = 0
		self.fm = file_manager
		self.spec = self._setupSpectrometer()
