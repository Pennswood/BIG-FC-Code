from science import laser_control
"""
Task: turn TLC to operations temperature, followed by turning on laser.
        This function can be expected to be continuously called until laser is warmed up.
Input: none
Output: Integer. 0 = laser warmed up, 1 = laser warming up, 2 = TLC warming module up, >2 = some sort of error.
"""


class Laser():
    laser_commands = laser_control.Laser()
    def warm_up_laser(self):
        # TODO
        return
    """
    """
    def laser_arm(self):
        self.laser_commands.arm()
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
    def __init__(self):
        # 0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing
        self.laser_commands = laser_control.Laser()
        self.states_laser = 0
