import random

class Laser():
    def receive_command(self, cmd):
        if self.cmd == "" and not cmd[:4] == ";LA:":
            return "Error: code incorrect"
        if not cmd[-4:] == "<CR>":  # code not complete
            self.cmd = cmd
            return None
        if cmd[:4] == ";LA:":  # new command coming in
            self.cmd = ""
        # code is completed
        cmd = self.cmd + cmd
        self.cmd = ""
        cmd = cmd[4:][:-4]

    def __init(self):
        self.cmd = ""
        # 0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing, 6 = laser disconnected
        self.state = 0
        self. state
        return