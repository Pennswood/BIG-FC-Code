#!/usr/bin/python3
import oasis_serial


class TLC():
	
	# Returns an array of floats representing the temperatures of the thermisters
	def get_temperatures(self):
		self.serial_connection.sendBytes(b'\x02') #TODO: Replace this with the correct method of requesting the temperature data from the TLC
		return [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]

	# Returns an array of unsigned integers (0-255) representing the PWM duty cycle set on each heater
	def get_duty_cycles(self):
		self.serial_connection.sendBytes(b'\x03') #TODO: Replace this with the correct method of requesting the duty cycle data from the TLC
		return [0,0,0]
		
	# Sends a PING command to the TLC
	def ping(self):
		self.serial_connection.sendBytes(b'\x01') #TODO: Replace this with the correct PING command code
		# TODO: Implement a return value to indicate if the PING was successful or not

	# Must pass an OasisSerial object to the constructor. Represents the serial connection from the BBB to the TLC
	def __init__(self, serial_connection):
		self.tlc_serial = serial_connection