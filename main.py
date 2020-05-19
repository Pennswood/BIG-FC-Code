#!/usr/bin/python3
import time
import serial
import roverio as rover
import laserio as laser
import debug
import spectrometerio as spectrometer


#States:
#0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing
states_laser = 0
#False = standby, True = integrating
states_spectrometer = False

#False = storage mode, True = operations mode
states_TLC = False

files_transferring = False


def main_loop():
	"""This will be the main loop that checks for and processes commands"""
	print("Main loop entered")
	    command = read_command()
	    if command == 0:
	        rover.ping()
	    if command == 1:
	        laser.warm_up_laser()
	    if command == 2:
	        laser.laser_arm()
	    if command == 3
	        laser.laserlaser_disarm()
	    if command == 4:
	        laser.laser_fire()
	    if command == 5:
	        laser.laser_off()
	    if command == 6:
	        spectrometer.sample(10)
	    if command == 7:
	        spectrometer.sample(20)
	    if command == 8
	    	rover.all_spectrometer_data()
	    if command == 9:
	        rover.status_request()
	    if command == 10:
	        rover.status_dump()
	    if command == 11:
	        rover.manifest_request()
	    if command == 12:
	        rover.transfer_sample()
	    if command == 13:
	        clock_sync()
	    if command == 14:
	        pi_tune()
while(True):
	main_loop()
