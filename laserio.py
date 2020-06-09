"""
laserio.py
Manages the laser used for LIBS. Reads status/error codes from laser and handles initialization and arming.

Task:
		This function can be expected to be continuously called until laser is warmed up.
Input: none
Output: Integer. 0 = laser warmed up, 1 = laser warming up, 2 = TLC warming module up, >2 = some sort of error.

Random Notes:
1) Laser Enable – "This enables the laser and readies it for firing. Note: there will be an 8
second delay between when the laser is first enabled and the laser is able to fire." uJewel manual

2) Laser Status Bits:	Bit 15: Spare
						Bit 14: Spare
						Bit 13: High-Power Mode
						Bit 12: Low-Power Mode
						Bit 11: Ready To Fire				// Laser is enabled AND ready to fire. See note 1.
						Bit 10: Ready To Enable				// Proxy for laser is warmed up? Laser is warmed up and therefore CAN be enabled (armed/disarmed).
						Bit	 9: Power Failure (uhh boss, how do you tell me you've had a power failure when you don't have the power to respond? USB Power?)
						Bit	 8: Electrical Over Temp
						Bit	 7: Resonator Over Temp
						Bit	 6: External Interlock			// Not used?
						Bit	 5: Reserved
						Bit	 4: Reserved
						Bit	 3: Diode External Trigger
						Bit	 2: Reserved
						Bit	 1: Laser Active				// Laser is firing
						Bit	 0: Laser Enabled				// "laser is ready to fire". Armed/Disarmed state.

^^^This will be converted to a Sphinx table after I learn how to do that^^^

3) Confirm power mode with Science team

"""
from enum import IntEnum, Enum
import time
import threading

from oasis_config import DEBUG_MODE

if not DEBUG_MODE:
	import Adafruit_BBIO.GPIO as GPIO # Adafruit library for safe GPIO control
else:
	from debug import DummyGPIO as GPIO

from science import laser_control
import oasis_serial


class LASER_STATE(Enum):
	"""Possible Laser States. This is ***NOT*** the status value returned by pinging the laser."""
	OFF = 0
	WARMING_UP = 1
	WARMED_UP = 2
	ARMING = 3
	ARMED = 4
	FIRING = 5
	LASER_DISCONNECTED = 6
	OVERTEMP_ELECTRICAL = 7
	OVERTEMP_RESONATOR = 8
	POWER_FAILURE = 9

# Define the locations of the status bit
class LASER_STATUS_BITS(IntEnum):
	SPARE_1 = 15
	SPARE_2 = 14
	HIGH_POWER_MODE = 13
	LOW_POWER_MODE = 12
	READY_TO_FIRE = 11
	READY_TO_ENABLE = 10
	POWER_FAILURE = 9
	ELECTRICAL_OVERTEMP = 8
	RESONATOR_OVERTEMP = 7
	EXTERNAL_INTERLOCK = 6		# currently not checked in any function. Discuss with science if this could ever possibly be turned on by accident.
	RESERVED_5 = 5
	RESERVED_4 = 4
	DIODE_EXTERNAL_TRIGGER = 3
	RESERVED_2 = 2
	LASER_ACTIVE = 1
	LASER_ENABLED = 0

# Configure the laser mode
# When should we check this?
class LASER_CONFIG(Enum):
	ENERGY_MODE = 2			# High power. We barely have enough poewr to ablate with this level.
	DIODE_TRIGGER_MODE = 0	# Internal trigger, meaning we use commands to fire the laser rather than a GPIO pin.
	MODE = 1				# Single shot
	WARMUP_TIMER = 15	   	# wait 15 seconds before checking if warmup was successful

# declare array for the status bits (faster & uses less memory than list)
status_bit_array = [0] * 16

class Laser():


	# Laser is powered-up and DISARMED. While warming up, state is 1. When warmed up, state is 2.
	# need to laser inactive, laser disabled, laser not ready to fire, laser not ready to enable
	# 1) get the status
	# 2) check relevent status bits for hazards
	#	a) check if already warmed-up: ready-to-enable.
	#	b) check if beyond warm-up state: laser active, laser enabled, laser ready-to-fire
	# 3) if safe, send the warm-up command (send power to the laser)
	def warm_up_laser(self):
		status = self.get_status()	
		SBArray = self.get_status_array(status)
		self.oasis_serial.sendBytes(b'\x01')

		# Laser is already off. Perfect case so we don't need to check anything else. uC is active so we have data even though 48V is off.
		if (SBArray[LASER_STATUS_BITS.POWER_FAILURE] == 0 and SBArray[LASER_STATUS_BITS.RESONATOR_OVERTEMP] == 0 and SBArray[LASER_STATUS_BITS.ELECTRICAL_OVERTEMP] == 0 and SBArray[LASER_STATUS_BITS.LASER_ENABLED] == 0 and SBArray[LASER_STATUS_BITS.LASER_ACTIVE] == 0 and SBArray[LASER_STATUS_BITS.READY_TO_ENABLE] == 0 and SBArray[LASER_STATUS_BITS.READY_TO_FIRE] == 0):
			GPIO.output("P9_42", GPIO.HIGH)		# Set pin HIGH to enable 48V converter, and power up the laser
			self.oasis_serial.sendBytes(b'\x21')			# report that we are warming up
			warmupTimer = threading.Timer(LASER_CONFIG.WARMUP_TIMER, self.get_warmup_delay_status)
			warmupTimer.start()

		else:
			if (SBArray[LASER_STATUS_BITS.POWER_FAILURE] == 1):
				self.oasis_serial.sendBytes(b'\00') # error placeholder
			if(SBArray[LASER_STATUS_BITS.RESONATOR_OVERTEMP] == 1):
				self.oasis_serial.sendBytes(b'\00') # error placeholder
			if(SBArray[LASER_STATUS_BITS.ELECTRICAL_OVERTEMP] == 1):
				self.oasis_serial.sendBytes(b'\00') # error placeholder
			if(SBArray[LASER_STATUS_BITS.LASER_ENABLED] == 1):
				self.oasis_serial.sendBytes(b'\00') # placeholder
			if(SBArray[LASER_STATUS_BITS.LASER_ACTIVE] == 1):
				self.oasis_serial.sendBytes(b'\00') # placeholder
			if(SBArray[LASER_STATUS_BITS.READY_TO_FIRE] == 1):
				self.oasis_serial.sendBytes(b'\00') # placeholder
			if(SBArray[LASER_STATUS_BITS.READY_TO_ENABLE] == 1):
				self.oasis_serial.sendBytes(b'\00') #error placeholder
	"""
	"""
	# Laser is powered-up and ARMED. While arming, state is 3. When ARMED, state is 4.
	def laser_arm(self):
		self.laser_commands.arm()
		status = self.get_status()
		self.oasis_serial.sendBytes(b'\x01')
		if self.states_laser < 3:
			self.states_laser = 3	 # arming
		while status == 2:
			status = self.get_status()
		self.oasis_serial.sendBytes(b'\x20') # TODO: Fix from command.
		self.states_laser = 4

	"""
	"""
	# Laser is powered-up and DISARMED
	def laser_disarm(self):
		self.laser_commands.disarm()
		self.states_laser = 2				# WARMED UP
	"""
	"""
	# Laser must already be powered-up and ARMED to fire. When firing, state is 5.
	def laser_fire(self):
		self.laser_commands.fire_laser()
		self.states_laser = 5				# FIRING
	"""
	"""
	# Laser is powered-off. When off, state is 0.
	def laser_off(self):
		# TODO
		GPIO.output("P9_42", GPIO.LOW)	# set pin LOW to disable 48V converter, and thus the laser
		self.states_laser = 0				# OFF
		return

	"""
	Task: Gets the status response from the laser. Check Laser Status bits listed above.
	Input: None
	Output: Returns an integer: -1 = laser off (laser not responding), 0 = laser warming up (laser on/laser responding),
		2 = laser warmed up (ready to enable?), 3 = not used (arming = warmed up from the laser's perspective),
		4 = laser armed (laser enabled AND laser ready to fire), 5 = laser firing (laser active)
	"""
	# gets the status response of the laser
	def get_status(self):
		raw_status = self.laser_commands.get_status()
		return raw_status

	# gets a specific bit from the laser status response.
	# Pass it the response from the laser for status_response, and LASER_STATUS_BITS.whatever for the offset
	def get_status_bit(self, raw_status, offset):
		status_bit_value = (raw_status >> offset & 1)
		return status_bit_value

	# makes an array of status bits from the raw laser status response.
	def get_status_array(self, raw_status):
		for i in range(0, 15):
			status_bit_value = (raw_status >> i & 1)
			status_bit_array[i] = status_bit_value

		return status_bit_array

	def get_warmup_delay_status(self):
		retry_count = 0
		while retry_count < 2:
			status = self.get_status()
			if len(status) != 2:
				retry_count += 1
				time.sleep(5.0) # Wait for 5 seconds to try reading a response again
				continue

			warmup_status = self.get_status_bit(status, LASER_STATUS_BITS.READY_TO_ENABLE)
			if warmup_status == 1:
				self.oasis_serial.sendBytes(b'\x22')
			else:
				self.oasis_serial.sendBytes(b'\x21')
				time.sleep(5.0)
				if warmup_status == 1:
					self.oasis_serial.sendBytes(b'\x22')
				else:
					self.oasis_serial.sendBytes(b'\x21')	

	"""
	"""
	def __init__(self, oasis_serial):
		self.oasis_serial = oasis_serial
		self.laser_commands = laser_control.Laser()
		self.states_laser = 0
		self.timer = time.time()		# Only to initalize variable, not used.
		GPIO.setup("P9_42", GPIO.OUT)	# 48V enable is on P9_42. ON = GPIO HIGH. OFF = GPIO LOW.
		GPIO.output("P9_42", GPIO.LOW)	# make sure the laser is OFF
		CURRENT_LASER_STATE = 0			# initialize the laser state
