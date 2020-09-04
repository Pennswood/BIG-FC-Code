import unittest
from unittest.mock import Mock, patch
from base_spec_code import Spectrometer
import seabreeze.spectrometers

class TestSpectrometer(unittest.TestCase):
	"""
	This unittest class is used to test the Specctrometer functions.
	"""
	def setUp(self):
		"""
		This function sets up mock parameters for the Spectrometer and initializes the Spectrometer at the start of every test
		"""
		self.mock_fm = Mock()
		self.mock_serial = Mock()
		self.spec = Spectrometer(self.mock_serial, self.mock_fm)


	def tearDown(self):
		"""
		This function resets all the values for the variables initialized in setUp to prepare for the next test.
		It is called at the end of every test.
		"""
		self.mock_fm = None
		self.mock_serial = None
		self.spec = None


	def test_setup_no_spec(self):
		"""
		This test checks that if there is no spectrometer connected, there will never be a spectrometer
		"""
		# spectrometer already initialized in setUp
		self.assertTrue(self.spec.devices == [])
		self.assertIsNone(self.spec.spec)

		self.assertIsNone(self.spec._setup_spectrometer())  # sets up again to check again
		self.assertTrue(self.spec.devices == [])
		self.assertIsNone(self.spec.spec)


	# allow these methods to be mock methods and returns specified values
	@patch('base_spec_code.seabreeze.spectrometers.list_devices', return_value=['Spec1'])
	@patch('base_spec_code.seabreeze.spectrometers.Spectrometer', return_value=['SPEC'])  # need an object example to test this later
	def test_setup_with_spec(self, mock, mock2):
		"""
		This test checks that setup will be successful if there's something on the list
		"""
		# spectrometer was initialized before mock patch since it was in setUp
		self.assertTrue(self.spec.devices == [])
		self.assertIsNone(self.spec.spec)

		# sets up the spectrometer again with an actual list
		self.assertTrue(self.spec._setup_spectrometer() != None)
		self.assertTrue(mock.called)				# checks to see that the list devices was called
		self.assertTrue(mock2.called)				# checks to see that the Casating was called
		self.assertFalse(self.spec.devices == [])	# the list devices returned an actual list
		self.assertIsNone(self.spec.spec)			# Note: this is None because spec.spec wasn't set to the spectrometer

		self.spec.spec = self.spec._setup_spectrometer()	# sets self.spec to have an actual object
		self.assertFalse(self.spec.spec == None)			# shows that it does return something


	def test_set_trigger(self):
		"""
		This test checks that the trigger mode function is being called and that the value matches
		"""
		mock_trigger = Mock()
		self.spec.spec = mock_trigger
		self.spec.set_trigger(4)
		mock_trigger.trigger_mode.assert_called_with(4)


	def test_set_integration_time_micros(self):
		""""
		This test checks that the integration time is being set properly and calculated properly (from seconds to milliseconds)
		"""
		mock_integration = Mock()
		self.spec.spec = mock_integration
		self.spec.set_integration_time_micros(1000)

		mock_integration.integration_time_micros.assert_called_with(1000000)
		self.assertTrue(self.spec.integration_time == 1000000)
		self.assertFalse(self.spec.integration_time == 1000)

	# TODO: figure out how to read the other serial value
	def test_sample_send_serial_bytes(self):
		"""
		This test checks that the serial port is receiving the right value sent out by the Flight computer
		"""
		self.spec.oasis_serial = self.mock_serial
		self.spec.sample()
		self.spec.oasis_serial.sendBytes.assert_called_with(b'\x01')
		# self.spec.oasis_serial.sendBytes.assert_called_with(b'\x30')  # Needs a successful sample to work, should be tested in test_sample()


	# NOTE: check spectrum, see if there's a way to test and if it's correctly implemented from documentation
	@unittest.skip("Testing sample function needs some research and more work")
	def test_sample(self):
		"""
		This test checks that the data is being retrieved properly.
		"""
		self.assertFalse(self.spec.sample() == None)		#None means that it ran correctly, the error message may change
		# self.assertTrue(self.spec.sample() == 'Checking spectrometer connection')

		mock_spec = Mock()
		self.spec.spec = mock_spec
		self.spec.oasis_serial = self.mock_serial
		self.spec.sample()
		# check serial to make sure the correct bytes are being sent
		self.spec.oasis_serial.sendBytes.assert_called_with(b'\x01')
		self.spec.spec.spectrum.assert_called_with()
		self.spec.oasis_serial.sendBytes.assert_called_with(b'\x30')


	#TODO: look inside method
	def test_check_spec_conn(self):
		"""
		This test checks that the spectrometer connection is being reconnected properly.
		"""
		self.assertFalse(self.spec.check_spec_conn())
		self.assertFalse(self.spec.check_spec_conn())

		mock_spec_conn = Mock()
		mock_devices = Mock()
		self.spec.devices = [mock_devices]
		self.spec.spec = mock_spec_conn

		mock_devices.is_open = True 				# Treating the spectrometer as open
		self.assertTrue(self.spec.check_spec_conn())
		self.assertTrue(self.spec.devices[0].is_open)
		self.assertTrue(self.spec.devices != [])
		self.assertTrue(self.spec.spec is not None)

		mock_devices.is_open = False 				# Treating the spectrometer as closd/disconnected
		self.assertFalse(self.spec.check_spec_conn())
		self.assertFalse(self.spec.devices[0].is_open)
		self.assertTrue(self.spec.devices != [])
		self.assertTrue(self.spec.spec is not None)

		# TODO: can't test the scenario where it reconnects through the method due to being unable to change is_open during method

	#TODO: Look inside function
	@unittest.skip('may need magic mock to work')
	def test_spectrometer_integration_boundaries(self):
		"""
		This test checks that the boundaries are being read
		"""
		# Decide whether to keep initialize the self min max integration variable, if not use self.assertRaises
		mock_spec = Mock()
		self.spec.spec = mock_spec

		# self.assertIsNone(self.spec.min_integration_time)
		# self.assertIsNone(self.spec.min_integration_time)

		self.spec._spectrometer_integration_boundries()
		self.spec.specintegration_time_micros_limits.assert_called_with()


if __name__ == '__main__':
	unittest.main()
