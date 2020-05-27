#!/usr/bin/python3
import time
import serial
import roverio
import oasis_serial
import laserio as laser
import debug
import threading
import spectrometerio as spectrometer

#Set this to False when testing on the Beagle Bone Black
DEBUG_MODE = True

#States:
#0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing
states_laser = 0
#0 = standby, 1 = integrating, 2 = disconnected
states_spectrometer = 0

#False = storage mode, True = operations mode
states_TLC = False

files_transferring = False

#21X1 boolean array. False for non-active error, True for active errors
active_errors = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

#Last 2 rover commands. First being most recent, second next recent.
status = []

threads = []
def main_loop():
	"""This will be the main loop that checks for and processes commands"""
	#print("Main loop entered")
	command = rover_serial.readByte()
	
	#Adds the command into the status list
	status.insert(0, command)
	if len(status) > 2:
		status.pop(2)
	
	if command == b'\x01':
		roverio.ping(rover_serial)

	elif command == b'\x02':
		laser.warm_up_laser()

	elif command == b'\x03':
		laser.laser_arm()

	elif command == b'\x04':
		laser.laser_disarm()

	elif command == b'\x05':
		t1 = threading.Thread(target=spectrometer.sample, args=(10,))
		threads.append(t1)
		t1.start()
		t2 = threading.Timer(0.01, laser.laser_fire)

	elif command == b'\x06':
		laser.laser_off()

	elif command == b'\x07':
		spectrometer.sample(10)

	elif command == b'\x08':
		spectrometer.sample(20)

	elif command == b'\x09':
		roverio.all_spectrometer_data(rover_serial)

	elif command == b'\x0A':
		roverio.status_request(rover_serial)

	elif command == b'\x0B':
		roverio.status_dump(rover_serial)

	elif command == b'\x0C':
		roverio.manifest_request(rover_serial)

	elif command == b'\x0D':
		roverio.transfer_sample(rover_serial)

	elif command == b'\x0E':
		roverio.clock_sync(rover_serial)

	elif command == b'\xF0':
		roverio.pi_tune(rover_serial)

# Talk to Tyler to learn what this line does :)
rover_serial = oasis_serial.OasisSerial("/dev/ttyS1", debug_mode=DEBUG_MODE, debug_tx_port=roverio.ROVER_TX_PORT, debug_rx_port=roverio.ROVER_RX_PORT)

# Talk to Tyler to learn what this line does :)
tlc_serial = oasis_serial.OasisSerial("/dev/ttyS2", debug_mode=DEBUG_MODE, debug_tx_port=roverio.TLC_TX_PORT, debug_rx_port=roverio.TLC_RX_PORT)

while(True):
	main_loop()
