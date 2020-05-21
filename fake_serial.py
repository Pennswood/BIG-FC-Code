#!/usr/bin/python3
import socketserver
import threading

IP_ADDRESS = "127.0.0.1"
ROVER_PORT = 654
TLC_PORT = 321
BUFFER_SIZE = 1024

class RoverTCPHandler(socketserver.BaseRequestHandler):
	"""
	Simulates the Rover's response to the payload
	"""

	def handle(self):
		self.data = self.request.recv(BUFFER_SIZE)
		print("ROVER]\t Received data: " + str(self.data))


class TLCTCPHandler(socketserver.BaseRequestHandler):
	"""
	Simulates the TLC's response to the BBB
	"""

	def handle(self):
		self.data = self.request.recv(BUFFER_SIZE)
		print("TLC]\t Received data: " + str(self.data))

def main():
	global rover_sock, tlc_sock, ROVER_PORT, TLC_PORT
	print("Setting up TCP Rover socket...")
	rover_serv = socketserver.TCPServer((IP_ADDRESS, ROVER_PORT),RoverTCPHandler)

	print("Setting up TCP TLC socket....")
	tlc_serv = socketserver.TCPServer((IP_ADDRESS, TLC_PORT), TLCTCPHandler)

	rover_thread = threading.Thread(target=rover_serv.serve_forever)
	tlc_thread = threading.Thread(target=tlc_serv.serve_forever)

	print("Starting threads...")
	rover_thread.start()
	tlc_thread.start()

main()
