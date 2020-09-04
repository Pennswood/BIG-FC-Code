# TODO: figure out trigger mode issues. Currently not setting trigger mode anywhere so it defaults to 0.

"""
Manages communication with the spectrometer through the SeaBreeze library.
"""
import time
import seabreeze
import seabreeze.spectrometers


class Spectrometer():
	"""Class for interacting with the spectrometer through seabreeze."""

	def __init__(self, serial, file_manager):
		# 0 = standby, 1 = integrating, 2 = disconnected
		self.oasis_serial = serial
		# self.states_spectrometer = 0
		self.fm = file_manager
		self.devices = []
		self.spec = self._setup_spectrometer()

		self.trigger_mode = 0
		self.integration_time = 0


	def _setup_spectrometer(self):
		"""
		Set up method for the spectrometer.
		
		Returns
		-------
		object
			A spectrometer object
		None
			If an error occurs
		"""
		if self.devices == []:
			self.devices = seabreeze.spectrometers.list_devices()
		if self.devices != []:

			spec = seabreeze.spectrometers.Spectrometer(self.devices[0])
			return spec


		# print("ERROR: No spectrometer listed by seabreeze!")
		return None

	# TODO: check if parts of this function should be refactored (i.e. saving errors into the sample data)
	def sample(self):
		"""
		This function is used to signal the spectrometer to integrate for a set amount of time.

		Parameters
		----------
		milliseconds : int
			Inputted integration time for spectrometer
		"""
		try:
			self.oasis_serial.sendBytes(b'\x01') 						# Sending nominal responce
			wavelengths, intensities = self.spec.spectrum() 			# Returns wavelengths and intensities as a 2D array, and begins sampling
			data = wavelengths, intensities 							# Saving 2D array to variable data
			if intensities == [] or intensities == None:
				print('No data entered')								# Error handling for no data collected
			self.oasis_serial.sendBytes(b'\x30') 						# Code sent to spectrometer signaling sampling has successfully finished

			timestamp = time.time() 									# Returns # of seconds since Jan 1, 1970 (since epoch)
			self.fm.save_sample(timestamp, data) 						# Function call to create spectrometer file
		except:
			self.reconnect = True
			return 'Checking spectrometer connection'
		return None

	def set_trigger(self, num=0):
		"""
		This function allows for the user to set the trigger mode on the Flame-T spectrometer. 

		0 = Normal (Free-Running), 1 = Software, 2 = External Hardware Level Trigger, 3 = Normal (Shutter) Mode, 4 = External Hardware Edge Trigger
		"""
		self.spec.trigger_mode(num)

	def set_integration_time_micros(self, milliseconds):
		"""
		This function allows for the user to set the integration time on the Flame-T spectrometer.

		Parameters
		----------
		milliseconds : float
			The integration period the user specifies
		"""
		self.integration_time = milliseconds * 1000
		self.spec.integration_time_micros(milliseconds*1000)

	def _spectrometer_integration_boundries(self):
		"""
		This function allows for the user to set up their spectrometer class with the appropriate integration time limits.
		Also, you may extract a tuple of the min and max values from this function's return statement.

		Returns
		-------
		min_max : tuple
			A tuple with the minimum and maximum values as integers shown here: (min, max)
		"""
		min_max = self.spec.integration_time_micros_limits
		self.min_integration_time = min_max[0]
		self.max_integration_time = min_max[1]
		return min_max
		
	def check_spec_conn(self):
		"""
		This function will check if the spectrometer is connected and the connection is open. If it's not, it will attempt to reconnect it.
		Currently it will return a boolean for possible future use in error checking
		"""
		if self.devices == []:
			self.spec = self._setup_spectrometer()
		if self.devices != []:
			is_open = self.devices[0].is_open
			if is_open:
				return True
			else:
				# need try except because there will be an error if it tries to connect and the spectrometer isn't connected physically
				try:
					self.spec = self._setup_spectrometer()
				except:
					pass

			is_open = self.devices[0].is_open
			return is_open
		return False