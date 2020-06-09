"""
config.py
This module holds all global constants that may change frequently.
DO NOT IMPORT ANY OTHER MODULES FROM HERE.
This is meant to be a configuration file that any script can pull from.
It is to be lightweight and contain only constants.
"""

# Thermal Logic Controller
# Number of thermisters being used in the payload
THERMISTER_COUNT = 9

# Number of heaters that are driven independently
DUTY_CYCLE_COUNT = 1

# File Management
# File hierarchy constants
SD_PATH = Path("/mnt/SD/") # Path to where the SD card is mounted
DEBUG_SD_PATH = Path.cwd() / "debug_fs" / "SD/"

FLASH_PATH = Path("/home/debian/") # Path to where to store files on the flash
DEBUG_FLASH_PATH = Path.cwd() / "debug_fs" / "flash/"

# Logging
# Amount of time (seconds) between writing to status log file periodically
LOGGING_INTERVAL = 1

# Serial Communication
# Number of bytes that an integer (signed or unsigned) takes up.
INTEGER_SIZE = 4

# Baud rate that we communicate with the Rover at
ROVER_BAUD_RATE = 250000

# Baud rate that we communicate with the TLC at
TLC_BAUD_RATE = 9600

# Debugging
# The two value below are for debugging purposes only, they mean nothing to the TLC or BBB
ROVER_TX_PORT = 420 # Emulate sending to the Rover on this port
ROVER_RX_PORT = 421 # Emulate receiving from the Rover

TLC_TX_PORT = 320 # Emulate sending to the TLC on this port
TLC_RX_PORT = 321 # Emulate receiving from the TLC on this port

# Set this to False when testing on the Beagle Bone Black
DEBUG_MODE = True

DEBUG_BUFFER_SIZE = 1024
