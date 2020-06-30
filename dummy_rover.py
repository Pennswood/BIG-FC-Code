"""This module is used to simulate a rover interface with our flight computer"""
#!/usr/bin/python3
import threading
import time
import random
import oasis_serial
import ospp

from oasis_config import THERMISTER_COUNT, DUTY_CYCLE_COUNT, DEBUG_BUFFER_SIZE, ROVER_RX_PORT, ROVER_TX_PORT, TLC_RX_PORT, TLC_TX_PORT

IP_ADDRESS = "127.0.0.1"

done = False

def print_received(pm, prefix):
	""" Prints out the received DATA bytes from the BBB.

	Parameters
	----------
	oserial : object
		Oasis serial connection
	prefix : string
		The prefix to print before the DATA packet is printed.
	"""
	global done
	while not done:
		if len(pm._rx_buffer) > 0:
			a = pm._rx_buffer.pop()
			print(prefix + str(a))
			
def emulate_tlc_stream(tlc_serial):
	global done
	""" Creates a fake data stream that is sent to the BBB to emulate the TLC.

	Parameters
	----------
	tlc_serial : object
		TLC serial connection
	"""
	global THERMISTER_COUNT
	while not done:
		tlc_serial.send_string("|")
		for i in range(THERMISTER_COUNT):
			tlc_serial.send_string(str(random.random() * 400)[0:6] + ",") # send randomized thermister values
		tlc_serial.send_string(str(random.random())[0:6]) # send randomized duty cycle value
		time.sleep(1)
		
def main():
	""" Main loop for dummy rover
	"""
	global ROVER_RX_PORT, ROVER_TX_PORT, TLC_RX_PORT, done
	print("Setting up UDP sockets...")
	rover_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=ROVER_RX_PORT, debug_rx_port=ROVER_TX_PORT)
	pm = ospp.PacketManager(rover_serial)
	
	rover_print_data = threading.Thread(target=print_received, args=(pm,"BBB RX] "), daemon=True)
	rover_print_data.start()

	tlc_serial = oasis_serial.OasisSerial("/dev/null", debug_mode=True, debug_tx_port=TLC_RX_PORT, debug_rx_port=TLC_TX_PORT, rx_print_prefix="TLC RX] ")
	
	tlc_stream = threading.Thread(target=emulate_tlc_stream, args=(tlc_serial,))
	tlc_stream.daemon = True
	tlc_stream.start()

	constructing_packet = False
	packet = b''
	
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
			print("Custom Packet Manipulation:")
			print("\t:start_packet\tCreate a new, empty packet.")
			print("\t:send_packet\tSend the current packet to the BBB. Use the below pack commands to add data to the packet before sending.")
			print("\t:pack_ascii\tPack an ASCII string into the current packet")
			print("\t:pack_sint\tPack a signed integer into the current packet")
			print("\t:pack_uint\tPack an unsigned integer into the current packet")
			print("\t:pack_bytes\tPack a sequence of bytes into the current packet. Do not use \\x or 0x !")
			print("\t:pack_float\tPack an ASCII encoded float into the current packet. Do not use \\x or 0x !\n")
			
			#print("\t:tx_file\tSend the file at the given path to the payload")
			#print("\t:rx_file\tPrepare to receive a file from the payload, save to the given path")
			
		elif command == ":exit" or command == ":quit":
			done = True
		elif command == ":ping":
			ping_packet = ospp.DataPacket(b'\x01')
			pm.append(ping_packet)
		elif command == ":status":
			status_packet = ospp.DataPacket(b'\x0A')
			pm.append(status_packet)
		elif command == ":clk_sync":
			sync_packet = ospp.DataPacket(b'\x0E')
			sync_packet.pack_signed_integer(int(time.time()))
			pm.append(sync_packet)
		elif command == ":start_packet":
			if constructing_packet:
				print("Dropping old packet, starting new pne")
			packet = ospp.DataPacket(bytes.fromhex(input("Input packet code: ")))
			constructing_packet = True
		elif command == ":send_packet":
			if not constructing_packet:
				print("No packet to send. Please use :start_packet before this.")
			else:
				pm.append(packet)
				constructing_packet = False
		elif command == ":pack_ascii":
			if constructing_packet:
				packet.pack_ascii(input("Input string to pack and press enter:"))
			else:
				print("No packet started. Please use :start_packet before this.")
		elif command == ":pack_sint":
			if constructing_packet:
				packet.pack_signed_integer(int(input("Input integer: ")))
			else:
				print("No packet started. Please use :start_packet before this.")
		elif command == ":pack_uint":
			if constructing_packet:
				packet.pack_unsigned_integer(int(input("Input integer: ")))
			else:
				print("No packet started. Please use :start_packet before this.")
		elif command == ":pack_bytes":
			if constructing_packet:
				packet.pack_bytes(bytes.fromhex(input("Input bytes: ")))
			else:
				print("No packet started. Please use :start_packet before this.")
		elif command == ":pack_float":
			if constructing_packet:
				packet.pack_float(input("Input float:"))
			else:
				print("No packet started. Please use :start_packet before this.")
	
	pm.running = False
	tlc_stream.join()
	rover_print_data.join()

main()
