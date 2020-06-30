#!/usr/bin/python3
# pylint: disable=C0103
"""
Contains the main loop and rover command input processing code.
"""
import threading
from pathlib import Path

from repeated_timer import RepeatedTimer
import roverio
import file_manager
import oasis_serial
import oasis_config
import laserio
import spectrometerio
import error_checking
import debug
import ospp
from tlc import TLC

from oasis_config import ROVER_RX_PORT, ROVER_TX_PORT, TLC_RX_PORT,\
	TLC_TX_PORT, DEBUG_MODE, SD_PATH, DEBUG_FLASH_PATH, FLASH_PATH,\
	DEBUG_SD_PATH, LOGGING_INTERVAL, ROVER_BAUD_RATE, TLC_BAUD_RATE

# States:
files_transferring = False
files_transfer_thread = None

# 21X1 boolean array. False for non-active error, True for active errors.
# Goes from LSB to MSB where LSB is active_errors[0]
active_errors = [False, False, False, False, False, False, False, False, False, False, False,\
		False, False, False, False, False, False, False, False, False, False]

# Last 2 rover commands. First being most recent, second next recent.
past_two_commands = [b'\x00'] * 2

def main_loop():
	"""This will be the main loop that checks for and processes commands"""
	global active_errors, files_transferring, files_transfer_thread, packet_manager

	while len(packet_manager._rx_buffer) == 0:
		b = b''

	packet = packet_manager._rx_buffer.pop()
	command = packet.code.to_bytes(1, byteorder="big", signed=False)

	# Adds the command into the status list
	past_two_commands.insert(0, command)

	if len(past_two_commands) > 2:
		past_two_commands.pop(2)

	if not error_checking.is_valid_command(laser.states_laser,\
	spectrometer.states_spectrometer, active_errors, past_two_commands[0]):
		rover.send_cmd_rejected_response(laser.states_laser,\
			spectrometer.states_spectrometer, active_errors, past_two_commands[0])
		pass

	else:
		if command == b'\x01':
			rover.ping()
		elif command == b'\x02':
			threading.Thread(target=laser.warm_up_laser).start()
		elif command == b'\x03':
			threading.Thread(target=laser.laser_arm).start()
		elif command == b'\x04':
			laser.laser_disarm()
			threading.Thread(target=laser.laser_disarm).start()
		elif command == b'\x05':
			t1 = threading.Thread(target=spectrometer.sample, args=(10,))
			t2 = threading.Timer(0.001, laser.laser_fire)
			t1.start()
			t2.start()
		elif command == b'\x06':
			threading.Thread(target=laser.laser_off).start()

		elif command == b'\x07':
			threading.Thread(target=spectrometer.sample, args=(oasis_config.SPECTROMETER_SAMPLE_DURATION_MS,)).start()

		elif command == b'\x08':
			# depriciated
			pass
			# threading.Thread(target=spectrometer.sample, args=(20,)).start()

		elif command == b'\x09':
			files_transferring = True
			files_transfer_thread = threading.Thread(target=rover.all_spectrometer_data)
			files_transfer_thread.start()

		elif command == b'\x0A':
			rover.status_request(laser.states_laser, spectrometer.states_spectrometer,
					tlc.get_temperatures(), tlc.get_duty_cycles(), active_errors, past_two_commands[1])
		elif command == b'\x0B':  # RS422: Begin to use the rover line for extended period of time
			files_transferring = True
			files_transfer_thread = threading.Thread(target=rover.status_dump)
			files_transfer_thread.start()

		elif command == b'\x0D': # RS422: Begin to use the rover line for extended period of time
			files_transferring = True
			files_transfer_thread = threading.Thread(target=rover.transfer_sample)
			files_transfer_thread.start()
		elif command == b'\x0E':
			rover.clock_sync()

		elif command == b'\xF0':
			debug.pi_tune()

if DEBUG_MODE:
	fm = file_manager.FileManager(DEBUG_SD_PATH, DEBUG_FLASH_PATH)
else:
	fm = file_manager.FileManager(SD_PATH, FLASH_PATH)

# Set up our serial connection to the rover
rover_serial = oasis_serial.OasisSerial("/dev/ttyS1", debug_mode=DEBUG_MODE,
		debug_tx_port=ROVER_TX_PORT, debug_rx_port=ROVER_RX_PORT, rx_print_prefix="BBB RX] ")
# Set up a packet manager to process the OSPP packets we send and recieve
packet_manager = ospp.PacketManager(rover_serial)

tlc_serial = oasis_serial.OasisSerial("/dev/ttyS2", debug_mode=DEBUG_MODE,
		debug_tx_port=TLC_TX_PORT, debug_rx_port=TLC_RX_PORT)

tlc = TLC(tlc_serial)
rover = roverio.Rover(rover_serial, fm)
laser = laserio.Laser(oasis_serial=rover_serial)

spectrometer = spectrometerio.Spectrometer(serial=rover_serial, file_manager=fm)

def log_timer_callback():
	"""This is the callback function that repeatedly logs the current status to the status log."""
	status_array = rover.get_status_array(laser.states_laser, spectrometer.states_spectrometer,
			tlc.get_temperatures(), tlc.get_duty_cycles(),
			active_errors, past_two_commands[1])
	fm.log_status(status_array, 0)

log_data_timer = RepeatedTimer(LOGGING_INTERVAL, log_timer_callback)
log_data_timer.start()

while True:
	main_loop()

packet_manager.running = False