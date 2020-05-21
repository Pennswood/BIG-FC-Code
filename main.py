#!/usr/bin/python3
import time
import serial
from roverio import rover_serial
import laserio as laser
import debug
import threading
import spectrometerio as spectrometer

#Set this to False when testing on the Beagle Bone Black
DEBUG_SERIAL = True

#States:
#0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing
states_laser = 0
#False = standby, True = integrating
states_spectrometer = False

#False = storage mode, True = operations mode
states_TLC = False

files_transferring = False

threads = []
def main_loop():
	"""This will be the main loop that checks for and processes commands"""
	print("Main loop entered")
	command = rover.read_command()
	if command == '\x01':
		rover.ping()

	if command == '\x02':
		laser.warm_up_laser()

	if command == '\x03':
		laser.laser_arm()

	if command == '\x04':
		laser.laser_disarm()

	if command == '\x05':
		t1 = threading.Thread(target=spectrometer.sample, args=(10,))
		threads.append(t1)
		t1.start()
		t2 = threading.Timer(.01, laser.laser_fire)

	if command == '\x06':
		laser.laser_off()

	if command == '\x07':
		spectrometer.sample(10)

	if command == '\x08':
		spectrometer.sample(20)

	if command == '\x09':
		rover.all_spectrometer_data()

	if command == '\x0A':
		rover.status_request()

	if command == '\x0B':
		rover.status_dump()

	if command == '\x0C':
		rover.manifest_request()

	if command == '\x0D':
		rover.transfer_sample()

	if command == '\x0E':
		rover.clock_sync()

	if command == '\xF0':
		rover.pi_tune()


rover_serial = RoverSerial(DEBUG_SERIAL)

while(True):
	main_loop()
