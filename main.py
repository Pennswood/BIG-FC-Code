#!/usr/bin/python3
import time
import serial
import roverio
import sdcardio
import oasis_serial
import laserio
from tlc import TLC
import debug
import threading
import spectrometerio

#Set this to False when testing on the Beagle Bone Black

#SD Card constants
PATH = "/home/"
PATH_DEBUG = "files/"
PATH_TO_SD_CARD = "/mnt/"
PATH_TO_SD_CARD_DEBUG = "files/sd_card/"
LOG_BYTE_LENGTH = 44

#Rover IO constants
# The two value below are for debugging purposes only, they mean nothing to the TLC or BBB
ROVER_TX_PORT = 420  # Emulate sending to the Rover on this port
ROVER_RX_PORT = 421  # Emulate receiving from the Rover

TLC_TX_PORT = 320  # Emulate sending to the TLC on this port
TLC_RX_PORT = 321  # Emulate receiving from the TLC on this port

DEBUG_MODE = True

#States:
files_transferring = False

#21X1 boolean array. False for non-active error, True for active errors. Goes from LSB to MSB where LSB is active_errors[0]
active_errors = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

#Last 2 rover commands. First being most recent, second next recent.
status = []

#float array for temperature data
temp_data = []

#int array for etch foil duty cycle
efdc = []

threads = []
def main_loop():
	"""This will be the main loop that checks for and processes commands"""
	#print("Main loop entered")
	while rover_serial.in_waiting() == 0:
		a=''
		#just do nothing for now, we use this because the readByte call will repeatedly timeout
	command = rover_serial.readByte()
	
	#Adds the command into the status list
	status.insert(0, command)
	if len(status) > 2:
		status.pop(2)
	
	if command == b'\x01':
		rover.ping(rover_serial)

	elif command == b'\x02':
		laser.warm_up_laser()

	elif command == b'\x03':
		laser.laser_arm()

	elif command == b'\x04':
		laser.laser_disarm()

	elif command == b'\x05':
		"""t1 = threading.Thread(target=spectrometer.sample, args=(10,))
		threads.append(t1)
		t1.start()
		t2 = threading.Timer(0.01, laser.laser_fire)"""
		laser.laser_fire()

	elif command == b'\x06':
		laser.laser_off()

	elif command == b'\x07':
		spectrometer.sample(10)

	elif command == b'\x08':
		spectrometer.sample(20)

	elif command == b'\x09':
		rover.all_spectrometer_data(rover_serial)

	elif command == b'\x0A':
		# print("This still needs to be implemented")
		# print(tlc.get_temperatures())
		temp_data = tlc.get_temperatures()		# set the temp_data array to the most recent temp_data
		efdc = tlc.get_duty_cycles()			# set the efdc array to the most recent efdc
		status_array = rover.get_status_array(states_laser, states_spectrometer, temp_data, efdc, active_errors, status[1])
		rover.status_request(rover_serial, status_array)

		#roverio.status_request(rover_serial)
		#rover_serial.sendBytes(roverio.get_status_array(states_laser, states_spectrometer, 

	elif command == b'\x0B':
		rover.status_dump(rover_serial)

	elif command == b'\x0C':
		rover.manifest_request(rover_serial)

	elif command == b'\x0D':
		rover.transfer_sample(rover_serial)

	elif command == b'\x0E':
		rover.clock_sync(rover_serial)

	elif command == b'\xF0':
		rover.pi_tune(rover_serial)
		
	elif command == b'\x75':
		rover_serial.sendFile(open("test.txt", "rb"), "test.txt")

# Talk to Tyler to learn what this line does :)
rover_serial = oasis_serial.OasisSerial("/dev/ttyS1", debug_mode=DEBUG_MODE, debug_tx_port=ROVER_TX_PORT, debug_rx_port=ROVER_RX_PORT, rx_print_prefix="BBB RX] ")

# Talk to Tyler to learn what this line does :)
tlc_serial = oasis_serial.OasisSerial("/dev/ttyS2", debug_mode=DEBUG_MODE, debug_tx_port=TLC_TX_PORT, debug_rx_port=TLC_RX_PORT, rx_print_prefix="BBB TLC RX] ")
tlc = TLC(tlc_serial)

laser = laserio.laser()
spectrometer = spectrometerio.spectrometer()
if DEBUG_MODE:
	sdcard = sdcardio.sdcard(path=PATH_DEBUG, path_to_sd_card=PATH_TO_SD_CARD_DEBUG, log_byte_length=LOG_BYTE_LENGTH)
else:
	sdcard = sdcardio.sdcard(path=PATH, path_to_sd_card=PATH_TO_SD_CARD, log_byte_length=LOG_BYTE_LENGTH)

rover = roverio.rover(sdcard=sdcard,ROVER_TX_PORT=ROVER_TX_PORT, ROVER_RX_PORT = ROVER_RX_PORT, TLC_TX_PORT = TLC_TX_PORT, TLC_RX_PORT = TLC_RX_PORT)

while(True):
	main_loop()
