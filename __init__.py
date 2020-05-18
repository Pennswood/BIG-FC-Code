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
    if command == 0:
        ping()
    if command == 1:
        warm_up_laser()
    if command == 2:
        laser_arm()
    if command == 3
        laser_disarm()
    if command == 4:
        laser_fire()
    if command == 5:
        lsaer_off()
    if command == 6:
        sample(10)
    if command == 7:
        sample(20)
    if command == 8
    all_spectrometer_data()
    if command == 9:
        status_request()
    if command == 10:
        status_dump()
    if command == 11:
        manifest_request()
    if command == 12:
        transfer_sample()
    if command == 13:
        clock_sync()
    if command == 14:
        pi_tune()
