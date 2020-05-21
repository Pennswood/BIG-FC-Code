#!/usr/bin/python3
import oasis_serial
import threading

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

def main():
	global ROVER_RX_PORT, ROVER_TX_PORT, TLC_RX_PORT
	print("Setting up UDP sockets...")
	rover_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=ROVER_TX_PORT, debug_rx_port=ROVER_RX_PORT)

	tlc_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=TLC_TX_PORT, debug_rx_port=TLC_RX_PORT)
	
	rover_print_thread = threading.Thread(target=print_received, args=(rover_serial,"ROVER"))
	tlc_print_thread = threading.Thread(target=print_received, args=(tlc_serial,"TLC"))
	
	rover_print_thread.daemon = True
	tlc_print_thread.daemon = True
	
	rover_print_thread.start()
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
			print("\t:status\t\tSend a STATUS REQUEST command the BBB\n")
			print("\t:send_ascii\tSend an ASCII string the BBB")
			print("\t:send_sint\tSend a signed integer to the BBB")
			print("\t:send_uint\tSend an unsigned integer to the BBB")
			
		elif command == ":exit" or command == ":quit":
			done = True
		elif command == ":ping":
			rover_serial.sendBytes(b'\x01')
		elif command == ":status":
			rover_serial.sendBytes(b'\x0A')
		elif command == ":send_ascii":
			rover_serial.sendString(input("Input string to send and press enter:"))
		elif command == ":send_sint":
			rover_serial.sendSignedInteger(int(input("Input integer: ")))
		elif command == ":send_uint":
			rover_serial.sendUnsignedInteger(int(input("Input integer: ")))
		
main()
