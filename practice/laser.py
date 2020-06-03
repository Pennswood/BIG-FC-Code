import random

class Laser():
    def receive_command(self, cmd):
        if not self.state == 0:
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
            if cmd[:-1] == "?":
                # TODO: add more commands to test more/ MIN/MAX commands.
                # Request
                if cmd[:2] == "SS":
                    return str(self.status)+"<CR>"
                if cmd[:2] == "FL":
                    return str(self.fire_laser) + "<CR>"
                if cmd[:2] == "EN":
                    return str(self.enable) + "<CR>"
                if cmd[:2] == "PM":
                    return str(self.mode) + "<CR>"
                if cmd[:2] == "RR":
                    if cmd[-4:] == "MIN?":
                        return str(1) + "<CR>"
                    if cmd[-4:] == "MAX?":
                        return str(5) + "<CR>"
                    return str(self.repetition_rate) + "<CR>"
                if cmd[:2] == "BC":
                    return str(self.burst_count) + "<CR>"
                if cmd[:2] == "DC":
                    if cmd[-4:] == "MIN?":
                        return str(0) + "<CR>"
                    if cmd[-4:] == "MAX?":
                        return str(.5) + "<CR>"
                    return str(self.diode_current) + "<CR>"
                if cmd[:2] == "EM":
                    return str(self.energy_mode) + "<CR>"
                if cmd[:2] == "DW":
                    if cmd[-4:] == "MIN?":
                        return str(.1) + "<CR>"
                    if cmd[-4:] == "MAX?":
                        return str(.2) + "<CR>"
                    return str(self.diode_width) + "<CR>"
                if cmd[:2] == "DT":
                    return str(self.diode_trigger_mode) + "<CR>"
            else:
                if cmd[:2] == "FL":
                    return self.laser_fire(int(cmd.split()[1]))
                if cmd[:2] == "EN":
                    self.laser_enable(int(cmd.split()[1]))
                if cmd[:2] == "PM":
                    self.laser_mode(int(cmd.split()[1]))
                if cmd[:2] == "RR":
                    self.laser_rep_rate(float(cmd.split()[1]))
                if cmd[:2] == "BC":
                    self.laser_burst_count(int(cmd.split()[1]))
                if cmd[:2] == "DC":
                    self.laser_diode_current(float(cmd.split()[1]))
                if cmd[:2] == "EM":
                    self.laser_energy_mode(int(cmd.split()[1]))
                if cmd[:2] == "DW":
                    self.laser_diode_width(float(cmd.split()[1]))
                if cmd[:2] == "DT":
                    self.laser_diode_trigger(int(cmd.split()[1]))
        else:
            return ""

    def laser_fire(self, cmd_code):
        #TODO
        return
    def laser_enable(self, cmd_code):
        #TODO
        return
    def laser_mode(self, cmd_code):
        pass

    def laser_rep_rate(self, cmd_code):
        pass

    def laser_burst_count(self, cmd_code):
        pass

    def laser_diode_current(self, cmd_code):
        pass

    def laser_energy_mode(self, cmd_code):
        pass

    def laser_diode_width(self, cmd_code):
        pass

    def laser_diode_trigger(self, cmd_code):
        pass
    def __init(self):
        self.cmd = ""
        # 0 = off, 1 = warming up, 2 = warmed up, 3 = arming, 4 = armed, 5 = firing, 6 = laser disconnected
        self.state = 0

        # -100000 = random number that we don't know. All other values are "default" values specified in the datasheet.
       # self.bank_voltage
        self.diode_current = -100000 #
        self.burst_count = 10 #
        self.diode_trigger_mode = 0 #
        self.diode_width = -100000 #
        self.echo = 0
        self.energy_mode = 2 #
        self.enable = 0 #
        self.fire_laser = 0 #
      #  self.fet_temp
        self.id = "test microjewel 0.0.0"
       # self.diode_current_value
       # self.pulse_period
        self.mode = 0 #
        self.repetition_rate = 1 #
        self.reset = None #This is not a variable, just a command
        # self.system_shot_count = 0
        self.status = 2 ** 13 # High power mode on. #
        self.user_shot_count = 0
        return

