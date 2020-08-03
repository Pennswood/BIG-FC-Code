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
		devices = seabreeze.spectrometers.list_devices()
		if devices != []:
			spec_error_bits[0] = 0
			spec = seabreeze.spectrometers.Spectrometer(devices[0])
			self.spectrometer_state.on_standby()
			return spec

		spec_error_bits[0] = 1
		self.spectrometer_state.spec_disconnect()
		print("ERROR: No spectrometer listed by seabreeze!")
		return None

	def sample(self, milliseconds):
		"""
		This function is used to signal the spectrometer to integrate for a set amount of time.

		Parameters
		----------
		milliseconds : int
			Inputted integration time for spectrometer
		"""
		
		try:
			self.spec.trigger_mode = 0 									# Setting the trigger mode to normal
			self.spec.integration_time_micros(milliseconds*1000) 		# Set integration time for spectrometer
			self.spectrometer_state.integrate()
			self.oasis_serial.sendBytes(b'\x01') 						# Sending nominal responce
			try:
				wavelengths, intensities = self.spec.spectrum() 		# Returns wavelengths and intensities as a 2D array, and begins sampling
				#spec_error_bits[2] = 0
			except:
				#spec_error_bits[2] = 1
				print('An error occurred while attempting to sample')  # using return would end the function
				# return 'An error occurred while attempting to sample' 	# Command to sample didn't work properly

			data = wavelengths, intensities 							# Saving 2D array to variable data
			if data == []:
				print('No data entered')								# using return would end the function
				# return 'No data entered' 								# Error handling for no data collected
			self.oasis_serial.sendBytes(b'\x30') 						# Code sent to spectrometer signaling sampling has successfully finished

			timestamp = time.time() 									# Returns # of seconds since Jan 1, 1970 (since epoch)
			self.fm.save_sample(timestamp, data) 						# Function call to create spectrometer file
			self.spectrometer_state.on_standby()
		except:
			self.spec_check_connection()
			return 'Attempting to Reconnect Spectrometer'
		return None

	# remade this function and called it check_spec_conn() below. All instances of this function will be commented out/deleted
	def spec_check_connection(self):
		"""
		This function checks the connection between the FC and the spectrometer. If the spectrometer is disconnected, \
			we will try 3 times to reconnect it to the FC.
		"""
		if self.spec == None:												# Checking if no spectrometer is listed
			self.spectrometer_state.spec_disconnect()
			for _ in range(3):
				try:
					self.spec = self._setupSpectrometer()					# Try setting up our spectrometer again
					if not self.spectrometer_state.is_spec_disconnected:	# If it's on standby, then our spectrometer is set up
						break
				except:
					continue
		return None

	# this function should be threaded to run in main, use the repeatedTimer already implemented for logging, inserted at line 129 at a later time
	def check_spec_conn(self, milliseconds):
		"""
		This function will repeatedly check if the spectrometer is connected. If it's not, it will attempt to reconnect it.
		"""
		if self.spectrometer_state.is_integrating:
			return None

		try:
			self.spec.integration_time_micros(milliseconds * 1000)
			'''
			There's another function is_open in the API backend. It's currently untested but may be a better alternative
			'''
		except Exception as e:
			print(e)
			try:
				# Would this possibly solve the issue of connecting the spectrometer twice
				# self.spec = None  
				self.spec = self._setupSpectrometer()
			except Exception as e:	# This should never happen
				print('Something is wrong with the setup Spectrometer function!!!')  # There should be no errors... hopefully
				print("The ERROR is: ", end = '')
				print(e)  # if the error does occur, it should be printed for debugging
		return None

	def __init__(self, serial, file_manager, spectrometer_state):
		# 0 = standby, 1 = integrating, 2 = disconnected
		self.oasis_serial = serial
		self.states_spectrometer = 0
		self.fm = file_manager
		self.spec = self._setupSpectrometer()
		self.spectrometer_state = spectrometer_state