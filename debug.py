"""
Contains utility functions for debugging, and possibly commands to use
during testing.
"""
def pi_tune():
	"""Attempts to automatically tune the PI loop."""
	print("TO BE IMPLEMENTED") # TODO
	return
	
class DummyGPIO():
	"""This class simulates dummy GPIO pins"""
	OUT = "OUT"
	# TODO: Is there an IN pin mode?
	LOW = "LOW"
	HIGH = "HIGH"

	@staticmethod
	def setup(pin_number, pin_mode):
		print("GPIO] Setting pin " + pin_number + " to mode " + pin_mode)
	
	@staticmethod
	def output(pin_number, value):
		print("GPIO] Writing " + value + " to pin " + pin_number)