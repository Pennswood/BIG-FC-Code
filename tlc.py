#!/usr/bin/python3
"""
tlc.py
Handling communication and data processing with the Thermal Logic Controller (TLC)
"""
import threading
import time

THERMISTER_COUNT = 9
DUTY_CYCLE_COUNT = 1

def read_tlc_stream(tlc):
	"""Thread loop that continuously reads the stream of serial data from the TLC"""
	while tlc.running:
		while tlc.tlc_serial.in_waiting() == 0:
			a = b'' # do nothing
		b = tlc.tlc_serial.readByte()

		# The read timed out, either connection is down or we have not started the TLC emulator
		if b is None:
			continue

		if b.decode('ascii') == "|":
			# Found start character, start reading stream data

			# 6 chars for temperature, and 1 char for comma, 5 chars for duty cycle
			s, tout = tlc.tlc_serial.readBytes((THERMISTER_COUNT*7) + 5)
			if tout:
				print("WARNING: Timed-out while reading TLC data stream!")
			else:
				s = s.decode("ascii")
				parts = s.split(",")
				if not len(parts) == THERMISTER_COUNT + 1:
					print("WARNING: Malformed TLC data! Skipping this reading...")
				else:
					tlc.read_lock.acquire()
					for i in range(THERMISTER_COUNT):
						tlc.temperatures[i] = float(parts[i])


					for i in range(THERMISTER_COUNT, DUTY_CYCLE_COUNT):
						tlc.duty_cycles[i] = float(parts[i])

					tlc.read_timestamp = time.time()
					tlc.read_lock.release()

class TLC():
	"""Class to handle communication and data collection of the Thermal Logic Controller (TLC)."""

	def getTemperatures(self):
		"""Returns an array of floats representing the temperatures of the thermisters in Kelvin"""
		self.read_lock.acquire()
		t = self.temperatures
		self.read_lock.release()
		return t

	def getDutyCycles(self):
		"""Returns an array of unsigned integers (0-255) representing
		the PWM duty cycle set on each heater"""
		self.read_lock.acquire()
		d = self.duty_cycles
		self.read_lock.release()
		return d

	def getData(self):
		"""Returns a tuple representing the most recent data from the TLC.
		A tuple: array of floats of temperatures in Kelvin, array of integers
		of duty cycle (0 to 255), and the timestamp of the last update
		"""
		self.read_lock.acquire()
		d = self.duty_cycles
		t = self.temperatures
		s = self.read_timestamp
		self.read_lock.release()
		return t, d, s

	def ping(self):
		"""Sends a PING command to the TLC"""
		self.tlc_serial.sendBytes(b'\x01') #TODO: Replace this with the correct PING command code
		# TODO: Implement a return value to indicate if the PING was successful or not

	# Must pass an OasisSerial object to the constructor.
	# Represents the serial connection from the BBB to the TLC
	def __init__(self, serial_connection):
		self.tlc_serial = serial_connection
		self.read_lock = threading.Lock()

		self.duty_cycles = [0] * DUTY_CYCLE_COUNT
		self.temperatures = [0.0] * THERMISTER_COUNT
		self.read_timestamp = time.time()

		self.running = True # set this to true to make the other thread join
		self.reading_thread = threading.Thread(target=read_tlc_stream, args=(self,))
		self.reading_thread.daemon = True
		self.reading_thread.start()

	def __del__(self):
		self.running = False
		self.reading_thread.join()
