#!/usr/bin/python3
import oasis_serial
import threading
import time

IP_ADDRESS = "127.0.0.1"
ROVER_RX_PORT = 420 # Emulate receiving from the BBB on this port (we are the Rover)
ROVER_TX_PORT = 421 # Emulate sending to the BBB on this port

TLC_RX_PORT = 320 # Emulate receiving from the BBB on this port (we are the TLC)
TLC_TX_PORT = 321 # Emulate sending to the BBB on this port

BUFFER_SIZE = 1024

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

def handle_rover_received(oserial, prefix):
	while True:
		oserial.rx_buffer_lock.acquire()
		d=bytearray()
		while len(oserial.rx_buffer) > 0:
			d += oserial.rx_buffer
			oserial.rx_buffer.clear()
		oserial.rx_buffer_lock.release()
		if d != b'':
			print("ROVER RX]\t" + str(bytes(d)))

def main():
	global ROVER_RX_PORT, ROVER_TX_PORT, TLC_RX_PORT
	print("Setting up UDP sockets...")
	rover_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=ROVER_TX_PORT, debug_rx_port=ROVER_RX_PORT)

	tlc_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=TLC_TX_PORT, debug_rx_port=TLC_RX_PORT)
	
	rover_handle_thread = threading.Thread(target=handle_rover_received, args=(rover_serial,"ROVER"))
	tlc_print_thread = threading.Thread(target=print_received, args=(tlc_serial,"TLC"))
	
	rover_handle_thread.daemon = True
	tlc_print_thread.daemon = True
	
	rover_handle_thread.start()
	tlc_print_thread.start()
	
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
			f = open(fname, "wb")
			rover_serial.receiveFile(f)
		time.sleep(0.5)
main()
