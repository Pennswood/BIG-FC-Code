#0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing
states_laser = 0
#False = standby, True = integrating
states_spectrometer = False

#False = storage mode, True = operations mode
states_TLC = False

files_transferring = False

"""
Task: checks for existing rover command and read command if it exists
Inputs: none
Returns: an integer value for the command number sent, or -1 for no commands sent
"""
def read_command():

"""
Task: writes a response to the rover.
Input: array of hex numbers to be sent to the rover,
with the number in index 1 to be sent first and last index sent last.
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
"""
def write_response(response):

"""
Task: sends a response to the rover.
Input: none
Returns: a boolean value, True for success and False for unsuccessful (line occupied, etc for debugging purposes)
"""
def ping():
    return write_response(hex(0x01))

"""
Task: turn TLC to operations temperature, followed by turning on laser.
        This function can be expected to be continuously called until laser is warmed up.
Input: none
Output: Integer. 0 = laser warmed up, 1 = laser warming up, 2 = TLC warming module up, >2 = some sort of error.
"""
def warm_up_laser():

"""
"""
def arm_laser():

"""
"""
def disarm_laser():

"""
"""
def fire_laser():

"""
"""
def laser_off():

"""
"""
def sample(milliseconds):

"""
"""
def all_spectrometer_data():

"""
"""
def status_request():

"""
"""
def status_dump():

"""
"""
def manifest_request():

"""
"""
def transfer_sample():

"""
"""
def clock_sync():

"""

"""
def pi_tune():


#Main code:
while(True):
    command = read_command()
    if(command == 0)
        ping()
    if(command == 1)
        warm_up_laser()
        
