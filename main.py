#!/usr/bin/python3
import time
import serial
import threading
from pathlib import Path

import debug
import roverio
import file_manager
import oasis_serial
import laserio
import spectrometerio
import error_checking
from tlc import TLC

# File hierarchy constants
SD_PATH = Path("/mnt/SD/") # Path to where the SD card is mounted
DEBUG_SD_PATH = Path.cwd() / "debug_fs" / "SD/"

FLASH_PATH = Path("/home/debian/") # Path to where to store files on the flash
DEBUG_FLASH_PATH = Path.cwd() / "debug_fs" / "flash/"

# Amount of time (seconds) between writing to status log file periodically
LOGGING_INTERVAL = 1

# Rover IO constants
# The two value below are for debugging purposes only, they mean nothing to the TLC or BBB
ROVER_TX_PORT = 420  # Emulate sending to the Rover on this port
ROVER_RX_PORT = 421  # Emulate receiving from the Rover

TLC_TX_PORT = 320  # Emulate sending to the TLC on this port
TLC_RX_PORT = 321  # Emulate receiving from the TLC on this port

# Set this to False when testing on the Beagle Bone Black
DEBUG_MODE = True

# States:
files_transferring = False

# 21X1 boolean array. False for non-active error, True for active errors. Goes from LSB to MSB where LSB is active_errors[0]
active_errors = [False, False, False, False, False, False, False, False, False, False, False, False, False, False,
				 False, False, False, False, False, False, False]

# Last 2 rover commands. First being most recent, second next recent.
status = [b'\x00'] * 2

def main_loop():
	global rover, rover_serial, laser, spectrometer, tlc,sdcard, active_errors
	"""This will be the main loop that checks for and processes commands"""
	
	while rover_serial.in_waiting() == 0:
		a = '' # just do nothing for now, we use this because the readByte call will repeatedly timeout
	
	command = rover_serial.readByte()

	# Adds the command into the status list
	status.insert(0, command)

	if len(status) > 2:
		status.pop(2)

	if not rover.is_valid_command(laser.states_laser, spectrometer.states_spectrometer, active_errors, status[0]):
		rover.send_cmd_rejected_response(laser.states_laser, spectrometer.states_spectrometer, active_errors, status[0])
	else:
		error_check = error_checking.ErrorCheck(laser_state = laser.states_laser, spec_state= spectrometer.states_spectrometer,
												error_state = active_errors, transfer_state = files_transferring, rover_comm = rover)
		if command == b'\x01':
			rover.ping()

		elif command == b'\x02':
			error_check.warm_up_check()
			laser.warm_up_laser()

		elif command == b'\x03':
			error_check.arm_check()
			laser.laser_arm()

		elif command == b'\x04':
			laser.laser_disarm()

		elif command == b'\x05':
			error_check.fire_check()
			laser.laser_fire()

		elif command == b'\x06':
			laser.laser_off()

		elif command == b'\x07':
			spectrometer.sample(10)

		elif command == b'\x08':
			spectrometer.sample(20)

		elif command == b'\x09':
			rover.all_spectrometer_data()

		elif command == b'\x0A':
			rover.status_request(laser.states_laser, spectrometer.states_spectrometer,
												  tlc.get_temperatures(), tlc.get_duty_cycles(),
												  active_errors, status[1])
		elif command == b'\x0B':
			rover.status_dump()

		elif command == b'\x0C':
			rover.manifest_request()

		elif command == b'\x0D':
			rover.transfer_sample()

		elif command == b'\x0E':
			rover.clock_sync()

		elif command == b'\xF0':
			debug.pi_tune()

		# TODO: remove!
		elif command == b'\x75':
			rover_serial.sendFile(open("test.txt", "rb"), "test.txt")

if DEBUG_MODE:
	fm = file_manager.FileManager(DEBUG_SD_PATH, DEBUG_FLASH_PATH)
else:
	fm = file_manager.FileManager(SD_PATH, FLASH_PATH)

# Talk to Tyler to learn what this line does :)
rover_serial = oasis_serial.OasisSerial("/dev/ttyS1", debug_mode=DEBUG_MODE, debug_tx_port=ROVER_TX_PORT,
										debug_rx_port=ROVER_RX_PORT, rx_print_prefix="BBB RX] ")

tlc_serial = oasis_serial.OasisSerial("/dev/ttyS2", debug_mode=DEBUG_MODE, debug_tx_port=TLC_TX_PORT,
									  debug_rx_port=TLC_RX_PORT)
tlc = TLC(tlc_serial)
rover = roverio.Rover(rover_serial, fm)
laser = laserio.Laser(oasis_serial = rover_serial)

spectrometer = spectrometerio.Spectrometer(serial = rover_serial, file_manager=fm)



#For logging file
def log_Timer_Callback():
	status_array = rover.get_status_array(laser.states_laser, spectrometer.states_spectrometer,
											  tlc.get_temperatures(), tlc.get_duty_cycles(),
											  active_errors, status[1])
	fm.log_status(status_array, 0)
	log_data_timer = threading.Timer(LOGGING_INTERVAL, function=log_Timer_Callback)
	log_data_timer.start()

log_data_timer = threading.Timer(LOGGING_INTERVAL, function=log_Timer_Callback) # Log our status every second
log_data_timer.start()

while (True):
	main_loop()
