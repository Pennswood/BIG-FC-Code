'''
Task: checks if the command sent is a valid command
Inputs: int for laser status, int for spectrometer status, 21X1 boolean array for active errors, bytes for command
Returns: Boolean of whether it's a valid command
'''
def is_valid_command(laser_status, spec_status, active_errors, cmd):
    if cmd == b'\x02': # warm up laser
        if active_errors[16] or active_errors[19] or active_errors[20]: #Excessive current draw, laser disconnected, temp high
            return False
    elif cmd == b'\x03': # Arm laser
        # NOTE: rover docs say not warmed up or firing which is redundant so firing is left out
        # TODO: this command should be allowed even if you are already armed or arming.

        #TODO: Considering allowing this state to be called even when firing, in which case it will stop the firing but stay armed.
        if laser_status != 2: # Laser is not in warmed up state
            return False
    elif cmd == b'\x04': # Laser disarm
        #TODO: this command should be allowed for all states except for "warming up" or "off.
        # (warmed up state, arming, armed, firing, are all allowed states to disarm)
        if laser_status != 2: # Laser is not in warmed up state
            return False
    elif cmd == b'\x05': #Fire laser
        if laser_status != 4: # Laser is not in armed state
            return False
    elif cmd == b'\x06': # Laser off
        # TODO: This command should be allowed in any state (as long as laser is not disconnected)
        if laser_status == 1: # Laser is not in on state
            return False
    elif cmd == b'\x07' or cmd == b'\x08': # Sample
        if spec_status == 1 or active_errors[16] or active_errors[18]: #Sampling, excessive current draw, or temp high.
            return False
    elif cmd == b'\x09' or cmd == b'\x0B' or cmd == b'\x0C' or cmd == b'\x0D': # Send files
        if laser_status != 0 or spec_status == 1: # laser not turned off or spectrometer integrating
            return False
    return True