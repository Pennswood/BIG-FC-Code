#!/usr/bin/python3

class Command():
	id = 0x00
	name = "COMMAND"
	def execute(self):
		print("This is the default command class!")
		return 0

class InvalidCommand():
	id = 0xFF
	name = "INVALID"
	def execute(self):
		print("Invalid command received!")
		return 0

class PingCommand():
	id = 0x01
	name = "PING"
	def execute(self):
		print("PONG")
		return 0

class TimeSync():
	id = 0x0E
	name = "CLOCK_SYNC"
	def execute(self):
		# TODO
		return
	def __init__(self, stream):
		#TODO
		return

def main():
	print("Enter command stream:")
	s = input()
	for c in s:
		if c == "p":
			p = PingCommand()
			p.execute()

main()
