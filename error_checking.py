class ErrorCheck:

    def arm_check(self):
        if self.spec_state == 1:
            self.rover.error_response(self.laser_state, self.spec_state, self.error_state, b'\x03')
            return False, "Error: Spectrometer is sampling, cannot arm."
        if self.laser_state == 0:
            self.rover.error_response(self.laser_state, self.spec_state, self.error_state, b'\x03')
            return False, "Error: Laser is off, cannot arm."
        if self.laser_state == 5:
            self.rover.error_response(self.laser_state, self.spec_state, self.error_state, b'\x03')
            return False, "Error: Laser is firing, cannot arm."
        return True, "States cleared"
    def warm_up_check(self):
        #TODO
        return
    def fire_check(self):
        #TODO
        return

    def __init__(self, laser_state, spec_state, error_state, transfer_state, rover_comm):
        self.laser_state = laser_state
        self.spec_state = spec_state
        self.error_state = error_state
        self.transfer_state = transfer_state
        self.rover = rover_comm