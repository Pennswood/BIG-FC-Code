from science import laser_control
import time
import Adafruit_BBIO.GPIO as GPIO       # Adafruit library for safe GPIO control
"""
Task: turn TLC to operations temperature, followed by turning on laser.
        This function can be expected to be continuously called until laser is warmed up.
Input: none
Output: Integer. 0 = laser warmed up, 1 = laser warming up, 2 = TLC warming module up, >2 = some sort of error.
"""


class Laser():
    # Laser is powered-up and DISARMED. While warming up, status is 1. When warmed up, status is 2.
    def warm_up_laser(self):
        status = self.get_status()
        self.oasis_serial(b'\x01')
        if self.states_laser < 1: # If the laser is already warmed up + armed, it can still run this command and not change anything
            self.states_laser = 1

        while status < 1: # We don't have a signal yet
            status = self.get_status()
        self.oasis_serial(b'\x23') # TODO: Fix from command.
        self.states_laser = 2

        GPIO.output("P9_42", GPIO.HIGH)     # Set pin HIGH to enable 48V converter, and thus the laser
        return
    """
    """
    # Laser is powered-up and ARMED. While arming, status is 3. When ARMED, status is 4.
    def laser_arm(self):
        self.laser_commands.arm()
        status = self.get_status()
        self.oasis_serial(b'\x01')
        if self.states_laser <3:
            self.states_laser = 3    # arming
        while status == 2:
            status = self.get_status()
        self.oasis_serial(b'\x20') # TODO: Fix from command.
        self.states_laser = 4
        return
    """
    """
    # Laser is powered-up and DISARMED
    def laser_disarm(self):
        self.laser_commands.disarm()
        return
    """
    """
    # Laser must already be powered-up and ARMED to fire. When firing, status is 5.
    def laser_fire(self):
        self.laser_commands.fire_laser()
        return
    """
    """
    # Laser is powered-off. When off, status is 0.
    def laser_off(self):
        # TODO

        GPIO.output("P9_42", GPIO.LOW)  # set pin LOW to disable 48V converter, and thus the laser
        return


    """
    Task: Gets the command from the laser.
    Input: None
    Output: Returns an integer: -1 = laser off (laser not responding), 0 = laser warming up (laser on/laser responding), 
        2 = laser warmed up (ready to enable?), 3 = not used (arming = warmed up from the laser's perspective),
        4 = laser armed (laser enabled AND laser ready to fire), 5 = laser firing (laser active)
    """
    def get_status(self):
        raw_status = self.laser_commands.get_status()
        # TODO: Some stuff
        output = 1
        return output
    """
    """
    def __init__(self, oasis_serial):
        self.oasis_serial = oasis_serial
        self.laser_commands = laser_control.Laser()
        # 0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing, 6 = laser disconnected
        self.states_laser = 0
        self.timer = time.time()        # Only to initalize variable, not used.
        GPIO.setup("P9_42", GPIO.OUT)   # 48V enable is on P9_42. ON = GPIO HIGH. OFF = GPIO LOW.
