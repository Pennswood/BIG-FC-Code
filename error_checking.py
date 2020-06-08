"""
Small module for ensuring that we can execute the requested command.
This should really be refactored into the main code.
"""
def is_valid_command(laser_status, spec_status, active_errors, cmd):
	'''
	Task: checks if the command sent is a valid command
	Inputs: int for laser status, int for spectrometer status, 21X1 boolean array for active errors, bytes for command
	Returns: Boolean of whether it's a valid command
	'''
	if cmd == b'\x02': # warm up laser
		if active_errors[16] or active_errors[19] or active_errors[20]: # Excessive current draw, laser disconnected, temp high
			return False
	elif cmd == b'\x03' or cmd == b'\x04': # Arm/disarm laser
		# TODO in laserio: this (arm) command should be allowed even if you are already armed or arming.
		# TODO in laserio: Considering allowing this (arm) state to be called even when firing, in which case it will stop the firing but stay armed.
		# TODO in laserio: this (disarm) command should be allowed for all states except for "warming up" or "off.
		# NOTE: If the laser is off, disconnected, or warming up, this command will be rejected
		if laser_status == 0 or laser_status == 1 or laser_status == 6: # Laser is not in warmed up state
			return False
	elif cmd == b'\x05': # Fire laser
		if laser_status != 4: # Laser is not in armed state
			return False
	elif cmd == b'\x06': # Laser off
		# TODO in laserio: This command should be allowed in any state (as long as laser is not disconnected)
		# NOTE: Original is "If the laser is not warmed up, or if it is in the process of warming up, this command will be rejected"
		# Now it's only "if the laser is disconnected, this command will be rejected", it will be allowed in any state
		if laser_status == 6: # Laser is disconnected
			return False
	elif cmd == b'\x07' or cmd == b'\x08': # Sample
		if spec_status == 1 or active_errors[16] or active_errors[18]: #Sampling, excessive current draw, or temp high.
			return False
	elif cmd == b'\x09' or cmd == b'\x0B' or cmd == b'\x0D': # Send files
		if laser_status != 0 or spec_status == 1: # laser not turned off or spectrometer integrating
			return False
	return True