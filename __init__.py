from debug import *
from roverio import *
from laserio import *
from spectrometerio import *


#States:
#0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing
states_laser = 0
#False = standby, True = integrating
states_spectrometer = False

#False = storage mode, True = operations mode
states_TLC = False

files_transferring = False






#Main code:
while(True):
    command = read_command()
    if(command == 0)
        ping()
    if(command == 1)
        warm_up_laser()
