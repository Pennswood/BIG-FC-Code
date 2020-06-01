from science import laser_control
import time
"""
Task: turn TLC to operations temperature, followed by turning on laser.
        This function can be expected to be continuously called until laser is warmed up.
Input: none
Output: Integer. 0 = laser warmed up, 1 = laser warming up, 2 = TLC warming module up, >2 = some sort of error.
"""


class Laser():
    def warm_up_laser(self):
        #TODO: we don't have correct GPIO pins yet for 48 VDc converter
        status = self.get_status()
        self.oasis_serial(b'\x01')
        while status == 1: # We don;t have a signal yet
            status = self.get_status()
        self.oasis_serial(b'\x23') # TODO: Fix from command.
        return
    """
    """
    def laser_arm(self):
        self.laser_commands.arm()
        status = self.get_status()
        self.oasis_serial(b'\x01')
        while status == 2:
            status = self.get_status()
        self.oasis_serial(b'\x20') # TODO: Fix from command.
        return
    """
    """
    def laser_disarm(self):
        self.laser_commands.disarm()
        return
    """
    """
    def laser_fire(self):
        self.laser_commands.fire_laser()
        return
    """
    """
    def laser_off(self):
        # TODO
        return


    """
    Task: Gets the command from the laser.
    Input: None
    Output: Returns an integer: 0 = laser off (laser not responding), 1 = laser warming up (laser on/laser responding), 
        2 = laser warmed up (ready to enable?), 3 = not used (arming = warmed up from the laser's perspective),
        4 = laser armed (laser enabled AND laser ready to fire), 5 = laser firing (laser active)
    """
    def get_status(self):
        raw_status = self.laser_commands.get_status()
        # TODO: Some stuff

        return


    def __init__(self, oasis_serial):
        self.oasis_serial = oasis_serial
        self.laser_commands = laser_control.Laser()
        # 0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing
        self.states_laser = 0
        self.timer = time.time() #Only to initalize variable, not used.
