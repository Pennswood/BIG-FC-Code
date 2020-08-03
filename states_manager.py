"""
Small module for ensuring that we can execute the requested command.
This should really be refactored into the main code.
"""

from statemachine import StateMachine, State

### State Classes ###

class Spectrometer_States(StateMachine):
	spec_disconnected = State('Spectrometer is Disconnected', initial = True)
	standby = State('Spectrometer on Standby')
	integrating = State('Spectrometer Integrating')

	integrate = standby.to(integrating)
	on_standby = standby.from_(spec_disconnected, integrating)
	spec_disconnect = spec_disconnected.from_(integrating, standby, spec_disconnected)

class Laser_States(StateMachine):
	laser_disconnected = State('Laser Disconnected', initial = True)
	off = State('Laser Off')
	on = State('Laser On')
	warming_up = State('Laser Warming Up')
	warmed_up = State('Laser Warmed Up')
	arming = State('Laser Arming')
	armed = State('Laser Armed')
	firing = State('Laser Firing')

	laser_turning_on = off.to(on)
	warming_command = on.to(warming_up)
	warming_finished = warming_up.to(warmed_up)
	arm_command = warmed_up.to(arming)
	arm_finished = arming.to(armed)
	fire_command = armed.to(firing)
	fire_finished = firing.to(armed)
	# need to find correct syntax for disarm and laser off command, StateMachine.current_state.to() doesn't work
	# disarm_command = StateMachine.current_state.to(warmed_up)
	# laser_off = StateMachine.current_state.to(off)

def is_valid_command(laser_status, spec_status, active_errors, cmd):
	'''
	Checks if the command sent is a valid command

	Parameters
	----------
	laser_status : int
		This integer value contains the current status of the laser
	
	spectrometer_status : int
		This integer value contains the current status of the spectrometer
	
	active_errors : list
		This is a 21x1 boolean array containing all active errors

	cmd : bytes
		This is the current command recieved from the rover
	
	Returns
	-------
	is_valid : bool
		Boolean of whether it's a valid command
	'''
	if cmd == b'\x02': # warm up laser
		if not laser.laser_state.is_off():
			return False
		# TODO: What happens if laser warming up state is active?
		elif active_errors[16] or active_errors[19] or active_errors[20]: # Excessive current draw, laser disconnected, temp high
			return False
	# Can't use docstrings to comment out elif statements, causes a syntax error
	# '''
	# elif cmd == b'\x03' or cmd == b'\x04': # Arm/disarm laser
	# 	# TODO in laserio: this (arm) command should be allowed even if you are already armed or arming.
	# 	# TODO in laserio: Considering allowing this (arm) state to be called even when firing, in which case it will stop the firing but stay armed.
	# 	# TODO in laserio: this (disarm) command should be allowed for all states except for "warming up" or "off.
	# 	# NOTE: If the laser is off, disconnected, or warming up, this command will be rejected
	# 	if laser_status == 0 or laser_status == 1 or laser_status == 6: # Laser is not in warmed up state
	# 		return False
	# '''
	elif cmd == b'\x03':	# arm command
		if laser.laser_state.is_off or laser.laser_state.is_warming_up or laser.laser_state.is_firing or laser.laser_state.is_laser_disconnected:
			return False

	elif cmd == b'\x04':	# disarm command
		if laser.laser_state.is_off or laser.laser_state.is_warming_up or laser.laser_state.is_warmed_up or laser.laser_state.is_arming or laser.laser_state.is_laser_disconnected:
			return False

	elif cmd == b'\x05': # Fire laser
		if not laser.laser_state.is_armed: # Laser is not in armed state
			return False

	elif cmd == b'\x06': # Laser off
		# TODO in laserio: This command should be allowed in any state (as long as laser is not disconnected)
		# NOTE: Original is "If the laser is not warmed up, or if it is in the process of warming up, this command will be rejected"
		# Now it's only "if the laser is disconnected, this command will be rejected", it will be allowed in any state
		if laser.laser_state.is_laser_disconnected: # Laser is disconnected
			return False
	elif cmd == b'\x07': # Sample
		if spectrometer.spectrometer_state.is_spec_disconnected:
			spectrometer.spec_check_connection()
			return False
		elif spectrometer.spectrometer_state.is_integrating or active_errors[16] or active_errors[18]: #Sampling, excessive current draw, or temp high.
			return False
	elif cmd == b'\x09' or cmd == b'\x0B' or cmd == b'\x0D': # Send files
		if not laser.laser_state.is_off or spectrometer.spectrometer_state.is_integrating: # laser not turned off or spectrometer integrating
			return False
	return True