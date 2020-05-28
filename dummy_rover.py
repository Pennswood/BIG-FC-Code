#!/usr/bin/python3
import oasis_serial
import threading
import time
import random

IP_ADDRESS = "127.0.0.1"
ROVER_RX_PORT = 420 # Emulate receiving from the BBB on this port (we are the Rover)
ROVER_TX_PORT = 421 # Emulate sending to the BBB on this port

TLC_RX_PORT = 320 # Emulate receiving from the BBB on this port (we are the TLC)
TLC_TX_PORT = 321 # Emulate sending to the BBB on this port

BUFFER_SIZE = 1024

THERMISTER_COUNT = 9 # Used to emulate the TLC stream

def print_received(oserial, prefix):
	while True:
		oserial.rx_buffer_lock.acquire()
		d=bytearray()
		while len(oserial.rx_buffer) > 0:
			d += oserial.rx_buffer
			oserial.rx_buffer.clear()
		oserial.rx_buffer_lock.release()
		if d != b'':
			print(prefix + " RX]\t" + str(bytes(d)))
			
def emulate_tlc_stream(tlc_serial):
	global THERMISTER_COUNT
	while True:
		tlc_serial.sendString("|")
		for i in range(THERMISTER_COUNT):
			tlc_serial.sendString(str(random.random() * 400)[0:6] + ",") # send randomized thermister values
		tlc_serial.sendString(str(random.random())[0:6]) # send randomized duty cycle value
		time.sleep(1)
		
def main():
	global ROVER_RX_PORT, ROVER_TX_PORT, TLC_RX_PORT
	print("Setting up UDP sockets...")
	rover_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=ROVER_TX_PORT, debug_rx_port=ROVER_RX_PORT, rx_print_prefix="ROVER RX] ")

	tlc_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=TLC_TX_PORT, debug_rx_port=TLC_RX_PORT, rx_print_prefix="TLC RX] ")
	
	tlc_stream = threading.Thread(target=emulate_tlc_stream, args=(tlc_serial,))
	tlc_stream.daemon = True
	tlc_stream.start()
	
	done = False
	while not done:
		print("\nEnter a command below, or enter ':help' for a list of available commands")
		command = input()
		if command == ":help":
			print("Help:\t\tAvailable Commands\n")
			print("\t:exit\t\tExits the program")
			print("\t:quit\t\tSame as :exit\n")
			print("\t:ping\t\tPing the BBB")
			print("\t:clk_sync\tSend a CLOCK SYNC command the BBB\n")
			print("\t:status\t\tSend a STATUS REQUEST command the BBB\n")
			print("\t:send_ascii\tSend an ASCII string the BBB")
			print("\t:send_sint\tSend a signed integer to the BBB")
			print("\t:send_uint\tSend an unsigned integer to the BBB")
			print("\t:send_bytes\tSend a sequence of bytes to the BBB. Do not use \\x or 0x !")
			print("\t:send_float\tSend an ASCII encoded float to the BBB. Do not use \\x or 0x !\n")
			print("\t:tx_file\tSend the file at the given path to the payload")
			print("\t:rx_file\tPrepare to receive a file from the payload, save to the given path")
			
		elif command == ":exit" or command == ":quit":
			done = True
		elif command == ":ping":
			rover_serial.sendBytes(b'\x01')
		elif command == ":status":
			rover_serial.sendBytes(b'\x0A')
		elif command == ":clk_sync":
			rover_serial.sendBytes(b'\x0E')
			rover_serial.sendSignedInteger(int(time.time()))
		elif command == ":send_ascii":
			rover_serial.sendString(input("Input string to send and press enter:"))
		elif command == ":send_sint":
			rover_serial.sendSignedInteger(int(input("Input integer: ")))
		elif command == ":send_uint":
			rover_serial.sendUnsignedInteger(int(input("Input integer: ")))
		elif command == ":send_bytes":
			rover_serial.sendBytes(bytes.fromhex(input("Input bytes: ")))
		elif command == ":send_float":
			rover_serial.sendFloat(float(input("Input float: ")))
		elif command == ":tx_file":
			fname = input("File to send:")
			f = open(fname, "rb")
			rover_serial.sendFile(f, fname)
		elif command == ":rx_file":
			fname = input("Location to save received file:")
			rover_serial.receiveFile(fname=fname)
		time.sleep(0.5)
main()
