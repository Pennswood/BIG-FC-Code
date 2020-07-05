**Oasis Constants**
===================

THERMISTER_COUNT
    (*int*) - This keeps track of the number of thermisters on Oasis. This should default to 9.

DUTY_CYCLE_COUNT
    (*int*) - This keeps track of the number of duty cycles taking place for our heaters

SD_PATH
    (*string*) - This is the path to which Oasis' micro sd card is mounted

DEBUG_SD_PATH
    (*string*) - For testing

FLASH_PATH
    (*string*) - Path to where to store files on our debian flash

DEBUG_FLASH_PATH
    (*string*) - For testing

LOGGING_INTERVAL
    (*int*) - The interval of time in which Oasis logs its status

LOGS_PER_FILE
    (*int*) - Number of status logs Oasis can fit into a single log file

STATUS_SIZE
    (*int*) - Length (in bytes) of a single status log

ROVER_BAUD_RATE
    (*int*) - Baud rate that Oasis communicates with the Rover at

TLC_BAUD_RATE
    (*int*) - Baud rate that Oasis communicates with the TLC at

