"""
This module holds all global constants that may change frequently.
This is meant to be a configuration file that any script can pull from.
It is to be lightweight and contain only constants. (See 7. Oasis Constants)
"""
from pathlib import Path


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
LOGGING_INTERVAL = 10

# How many status logs we can fit into a single log file
LOGS_PER_FILE = 200

#Spectrometer sample sizes
SPECTROMETER_SAMPLE_DURATION_MS = 4

SPECTROMETER_PIXEL_NUMBER = 3648
SPECTROMETER_DATA_SIZE = SPECTROMETER_PIXEL_NUMBER*4*2
#random number to get the number up to 500 bytes
PARITY_BYTES = 20816
TOTAL_SPECTROMETER_FILE_SIZE = SPECTROMETER_DATA_SIZE + PARITY_BYTES

# Length (in bytes) of a single status log
# Calculate size of status log entry: timestamp (4), thermisters (7 bytes each)
#heaters (1 byte each), laser status (1 byte), spectrometer status (1 byte)
#error flags (3 bytes), previous command (1 byte), log reason (1 byte)
STATUS_SIZE = 4 + (7 * THERMISTER_COUNT) + DUTY_CYCLE_COUNT + 1 + 1 + 3 + 1 + 1

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
