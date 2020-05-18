#!/usr/bin/python3
import time
import serial
import roverio
import laserio
import debug
import spectrometerio



def setup_serial():
	global roverSerial, tlcSerial
	roverSerial = serial.Serial("/dev/ttyS1")

def main_loop():
	"""This will be the main loop that checks for and processes commands"""
	print("Main loop entered")

main_loop()
