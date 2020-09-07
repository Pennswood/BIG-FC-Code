# TODO: figure out trigger mode issues. Currently not setting trigger mode anywhere so it defaults to 0.

"""
Manages communication with the spectrometer through the SeaBreeze library.
"""
import time
import seabreeze
import seabreeze.spectrometers
import threading

"""
IGNORE:		Spectrometer Error Bits (spec_error_bits)
										Bit 2: Spectrometer Data Failure (SDF)
										Bit 1: Spectrometer Disconnected (SDD)
										Bit 0: No Spectrometer Listed (NSL)
IGNORE
"""
spec_error_bits = [0, 1, 0]			# Spectrometer disconnected is a default state
ACQUISITION_DELAY = 0					# move this to a different file later on?

# TODO: Thread timer/wdt checking if spectrometer is still connected and if not set error bit to 1 (True)

class SpecConnWDT(Exception):
	pass

#TODO: Create some sort of error or boolean to know that external trigger is inactive
class Spectrometer():
	"""Class for interacting with the spectrometer through seabreeze."""

	def __init__(self, serial, file_manager, spectrometer_state):
		# 0 = standby, 1 = integrating, 2 = disconnected
		self.oasis_serial = serial
		# self.states_spectrometer = 0
		self.fm = file_manager
		self.devices = []
		self.spectrometer_state = spectrometer_state
		self.spec = self._setup_spectrometer()
		self.reconnect_counter = 0
		self._threads = []
		self.wdt_stop = False

		self.trigger_mode = 0
		self.integration_time = 0
		self.integration_time_left = 0
		self.acquire_time_left = False
		self.software_time_keeper_stop = False
		self.read_delay = 0

		self.past_data = []

		self.conn_wdt_thread = None
		self.software_timer_thread = None

	#TODO: initialize spectrometer integration time micros or create a default for it in the method
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

			# initialize initial values for spectrometer
			# self.set_acquisition_delay()
			# self.set_trigger()
			# self.set_integration_time_micros()
			return spec

		spec_error_bits[0] = 1
		self.spectrometer_state.spec_disconnect()
		print("ERROR: No spectrometer listed by seabreeze!")
		return None

	def _connection_wdt(self):
		"""
		This method is meant to be threaded and always running in the background.
		It continuously checks the status of our spectromter's connection to the BBB.
		"""
		while True:
			if self.wdt_stop == True:
				break
			if self.reconnect == True:
				response = self.check_spec_conn()
				self.reconnect_counter += 1
				if self.reconnect_counter >= 5:
					self.oasis_serial.sendBytes(b'\x00')	# TODO: Determine an error code for spectrometer having trouble connecting
			else:
				self.reconnect_counter = 0

			if response == True:
				self.reconnect_counter = 0
				self.reconnect = False
				self.oasis_serial.sendBytes(b'\x00')		# TODO: Determine a connection secured code to send to rover

			time.sleep(1)

	def _software_trigger_time_keeper(self):
		"""
		This method is meant to be threaded and running continuously in the background as a software trigger is initiated.
		This will keep track of where our software trigger's continuous integration cycle is at with the self.integration_time_left variable.
		"""
		self.spec.spectrum()								# Getting software trigger on track for integration cycle
		while True:
			start_time = time.time()
			while time.time() - start_time < (self.integration_time + self.read_delay):
				if self.acquire_time_left == True:
					self.integration_time_left = self.integration_time - (time.time() - start_time) 			# TODO: How is this going to work?
				if self.software_time_keeper_stop == True:
					break
			if self.software_time_keeper_stop == True:
				break

	def thread_controller(self, action):
		"""
		This is the control hub for all threads in the spectrometer class. Here you can start and terminate the WDT connection thread and software trigger time keeper thread.

		Action inputs correspond to these commands: 0 = Start WDT Thread, 1 = Kill WDT Thread, 2 = Start Software Time Keeper Thread, 3 = Kill Software Time Keeper Thread
		"""
		if action == 0 and self.conn_wdt_thread not in self._threads:
			self.wdt_stop = False														# This line will allow the thread to loop infinitely
			self.conn_wdt_thread = threading.Thread(target=self._connection_wdt)
			self.conn_wdt_thread.start()
			self._threads.append(self.conn_wdt_thread)									# Append WDT thread to list, in case we need to close the thread

		elif action == 1 and self.conn_wdt_thread in self._threads:
			self.wdt_stop = True														# This line will cause the WDT thread to terminate
			if self.conn_wdt_thread in self._threads:
				self._threads.pop(self._threads.index(self.conn_wdt_thread))			# Removing the terminated thread from active threads list

		elif action == 2 and self.software_timer_thread not in self._threads:
			self.software_time_keeper_stop = False
			self.software_timer_thread = threading.Thread(target=self._software_trigger_time_keeper)
			self.software_timer_thread.start()
			self._threads.append(self.conn_wdt_thread)

		elif action == 3 and self.software_timer_thread in self._threads:
			self.software_time_keeper_stop = True
			if self.software_timer_thread in self._threads:
				self._threads.pop(self._threads.index(self.software_timer_thread))

		elif action != 0 or action != 1 or action != 2 or action != 3:
			raise SpecConnWDT("Action command is not valid in connection WDT's state")

		else:
			raise SpecConnWDT("Action command is invalid")

	# TODO: check if parts of this function should be refactored (i.e. saving errors into the sample data)
	def sample(self):	# NOTE: Deleted milliseconds as it was not used in this function
		"""
		This function is used to signal the spectrometer to integrate for a set amount of time.

		Parameters
		----------
		milliseconds : int
			Inputted integration time for spectrometer
		"""
		try:
			self.spectrometer_state.integrate()
			self.oasis_serial.sendBytes(b'\x01') 						# Sending nominal response
			# NOTE: The proper delay must be added before this to ensure that the data retrieved is correct during external trigger
			wavelengths, intensities = self.spec.spectrum() 			# Returns wavelengths and intensities as a 2D array, and begins sampling
			data = wavelengths, intensities 							# Saving 2D array to variable data
			self.past_data = data 										# Store data for checking external trigger
			# This may not be necessary but to check if it's repeating instead
			if intensities == [] or intensities == None:
				print('No data entered')								# Error handling for no data collected
			self.oasis_serial.sendBytes(b'\x30') 						# Code sent to spectrometer signaling sampling has successfully finished

			timestamp = time.time() 									# Returns # of seconds since Jan 1, 1970 (since epoch)
			self.fm.save_sample(timestamp, data) 						# Function call to create spectrometer file
			self.spectrometer_state.on_standby()
		except:
			print('An error occurred while attempting to sample')  		# Command to sample didn't work properly
			self.reconnect = True
			return 'Checking spectrometer connection'
		return None

	def set_trigger(self, num=3):	# 3 is probably the external hardware edge trigger in the seabreeze library
		"""
		This function allows for the user to set the trigger mode on the Flame-T spectrometer. 

		0 = Normal (Free-Running), 1 = Software, 2 = External Hardware Level Trigger, 3 = Normal (Shutter) Mode, 4 = External Hardware Edge Trigger
		"""
		if num > 3:
			return None
		elif num < 0:
			return None
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

	#TODO: Check this function
	def set_acquisition_delay(self, microseconds=ACQUISITION_DELAY):
		"""
		This function allows for the user to set the acquisition delay in microseconds.
		"""
		self.spec.f.spectrometer.set_delay_microseconds(microseconds)

	#TODO: Will handle after unittests are complete
	def check_external_trigger(self):
		"""
		This function checks if the external trigger is working properly. It does so by comparing the past dataset to the new one
		"""
		pass

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