"""
Sends over the current status of the Oasis (temperature, error codes, laser and spectrometer status)
"""
def status_request(self):				# Is file a global var?
	self.sendBytes(self.tlc_mode)			# TLC mode | 1 byte
	self.sendBytes(self.laser_status)		# Laser status | 1 byte
	self.sendBytes(self.spec_status)		# Spectrometer status | 1 byte
	for i in temp_data:				# Assuming that temp_data is an array
        	self.sendBytes(i)			# Temperature data | 56 bytes
	for i in etch_foil_duty_cycle:	        	# Assuming EFDC is an array
        	self.sendBytes(i)			# Etch foil duty cycle | 3 bytes
	self.sendString(self.error_codes)		# Error codes | 3 bytes
	self.sendBytes(self.cmds_recieved)		# Commands received | 1 byte
	return None
