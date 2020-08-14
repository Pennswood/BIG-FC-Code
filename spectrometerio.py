# TODO: figure out trigger mode issues. Currently not setting trigger mode anywhere so it defaults to 0.

"""
Manages communication with the spectrometer through the SeaBreeze library.
"""
import time
import seabreeze
import seabreeze.spectrometers

"""
IGNORE:		Spectrometer Error Bits (spec_error_bits)
										Bit 2: Spectrometer Data Failure (SDF)
										Bit 1: Spectrometer Disconnected (SDD)
										Bit 0: No Spectrometer Listed (NSL)
IGNORE
"""
spec_error_bits = [0, 1, 0]			# Spectrometer disconnected is a default state

# TODO: Thread timer/wdt checking if spectrometer is still connected and if not set error bit to 1 (True)

class Spectrometer():
	"""Class for interacting with the spectrometer through seabreeze."""

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
			spec_error_bits[0] = 0
			spec = seabreeze.spectrometers.Spectrometer(self.devices[0])
			self.spectrometer_state.on_standby()
			return spec

		spec_error_bits[0] = 1
		self.spectrometer_state.spec_disconnect()
		print("ERROR: No spectrometer listed by seabreeze!")
		return None

	# TODO: check if parts of this function should be refactored (i.e. saving errors into the sample data)
	def sample(self, milliseconds):
		"""
		This function is used to signal the spectrometer to integrate for a set amount of time.

		Parameters
		----------
		milliseconds : int
			Inputted integration time for spectrometer
		"""
		try:
			# self.spec.trigger_mode = 0 									# Setting the trigger mode to normal
			self.spec.integration_time_micros(milliseconds*1000) 		# Set integration time for spectrometer
			self.spectrometer_state.integrate()
			self.oasis_serial.sendBytes(b'\x01') 						# Sending nominal responce
			wavelengths, intensities = self.spec.spectrum() 		# Returns wavelengths and intensities as a 2D array, and begins sampling
			print('An error occurred while attempting to sample')  	# Command to sample didn't work properly
			data = wavelengths, intensities 							# Saving 2D array to variable data
			# if data == []:
			if intensities == [] or intensities == None:
				print('No data entered')								# Error handling for no data collected
			self.oasis_serial.sendBytes(b'\x30') 						# Code sent to spectrometer signaling sampling has successfully finished

			timestamp = time.time() 									# Returns # of seconds since Jan 1, 1970 (since epoch)
			self.fm.save_sample(timestamp, data) 						# Function call to create spectrometer file
			self.spectrometer_state.on_standby()
		except:
			self.check_spec_conn()
			return 'Checking spectrometer connection'
		return None
		
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
				self.spectrometer_state.on_standby()
				return True
			else:
				# need try except because there will be an error if it tries to connect and the spectrometer isn't connected physically
				try:
					self.spec = self._setup_spectrometer()
				except:
					self.spectrometer_state.spec_disconnect()

			is_open = self.devices[0].is_open
			return is_open
		return False

	def __init__(self, serial, file_manager, spectrometer_state):
		# 0 = standby, 1 = integrating, 2 = disconnected
		self.oasis_serial = serial
		# self.states_spectrometer = 0
		self.fm = file_manager
		self.devices = []
		self.spec = self._setup_spectrometer()
		self.spectrometer_state = spectrometer_state
