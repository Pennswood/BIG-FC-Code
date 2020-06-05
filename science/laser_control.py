import serial
import serial.tools.list_ports
import time
import threading as thread


class Laser:
    def __init__(self):
        self.__ser = serial.Serial()
        self.pulseMode = None
        self.repRate = None
        self.burstCount = None
        self.diodeCurrent = None
        self.energyMode = None
        self.pulseWidth = None
        self.diodeTrigger = None
        self.autoArm = False
        self.burstDuration = 0

        self.__kicker_control = False  # False = off, True = On. Controls kicker for shots longer than 2 seconds
        self.__startup = True
        self.__threads = []
        self.__lock = thread.Lock()

    def __kicker(self):  # queries for status every second in order to kick the laser's WDT on shots >= 2s
        while True:
            if self.__kicker_control:
                self.__ser.write(';LA:SS?<CR>')
            time.sleep(1)

    def __send_command(self, cmd):  # sends command to laser
        last_line = self.__ser.readline()
        responses = []
        if not (isinstance(cmd, int) or isinstance(cmd, list) or isinstance(cmd, tuple)):
            raise TypeError("Error: command must be an integer, list, or tuple")
        if isinstance(cmd, list) or isinstance(list, tuple):
            for i in cmd:
                self.__ser.write(i)
                while True:
                    time.sleep(0.01)
                    response = self.__ser.readline()  # read response
                    if response:
                        responses.append(response)
                        break
        elif isinstance(cmd, str):
            self.__ser.write(cmd)
            while True:
                time.sleep(0.01)
                response = self.__ser.readline()
                if response:
                    break

    def connect(self, port_number, baud_rate=115200, timeout=5, parity=None):
        with self.__lock:
            if port_number not in serial.tools.list_ports.comports():
                raise ValueError(f"Error: port {port_number} is not available")
            self.__ser = serial.Serial(port=port_number)
            if baud_rate and isinstance(baud_rate, int):
                self.__ser.baudrate = baud_rate
            else:
                raise ValueError('Error: baud_rate parameter must be an integer')
            if timeout and isinstance(timeout, int):
                self.__ser.timeout = timeout
            else:
                raise ValueError('Error: timeout parameter must be an integer')
            if not parity or parity == 'none':
                self.__ser.parity = serial.PARITY_NONE
            elif parity == 'even':
                self.__ser.parity = serial.PARITY_EVEN
            elif parity == 'odd':
                self.__ser.parity = serial.PARITY_ODD
            elif parity == 'mark':
                self.__ser.parity = serial.PARITY_MARK
            elif parity == 'space':
                self.__ser.parity = serial.PARITY_SPACE
            else:
                raise ValueError("Error: parity must be None, \'none\', \'even\', \'odd\', \'mark\', \'space\'")
            if self.__startup:  # start kicking the laser's WDT
                t = thread.Thread(target=self.__kicker())
                self.__threads.append(t)
                t.start()
                self.__startup = False

    def fire_laser(self):
        with self.__lock:
            self.__send_command(';LA:FL 1<CR>')
            self.__send_command(';LA:SS?<CR>')
            if self.__ser.readline() != '3075<CR>':
                self.__send_command(';LA:FL 0<CR>')  # aborts if laser fails to fire
                raise RuntimeError('Laser Failed to Fire')
            else:
                if self.burstDuration >= 2:
                    self.__kicker_control = True
                time.sleep(self.burstDuration)
                self.__send_command(';LA:FL 0<CR>')

    def get_status(self):
        with self.__lock:
            self.__send_command(';LA:SS?<CR>')
            return self.__ser.read(2)            # laser is sending status as 2 bytes, so this needs to be read(2), not read() which takes in 1 byte by default

    def check_armed(self):
        with self.__lock:
            self.__send_command('LA:EN?<CR>')

    def arm(self):
        with self.__lock:
            self.__send_command(';LA:EN 1<CR>')

    def disarm(self):
        with self.__lock:
            self.__send_command(';LA:EN 0<CR>')

    def update_settings(self):
        # cmd format, ignore brackets => ;[Address]:[Command String][Parameters]<CR>
        with self.__lock:
            cmd_strings = list()
            cmd_strings.append(';LA:PM ' + str(self.pulseMode) + '<CR>')
            cmd_strings.append(';LA:RR ' + str(self.repRate) + '<CR>')
            cmd_strings.append(';LA:BC ' + str(self.pulseMode) + '<CR>')
            cmd_strings.append(';LA:DC ' + str(self.diodeCurrent) + '<CR>')
            cmd_strings.append(';LA:EM ' + str(self.energyMode) + '<CR>')
            cmd_strings.append(';LA:PM ' + str(self.pulseMode) + '<CR>')
            cmd_strings.append(';LA:DW ' + str(self.pulseWidth) + '<CR>')
            cmd_strings.append(';LA:DT ' + str(self.pulseMode) + '<CR>')

            for i in cmd_strings:
                self.__send_command(i)


def list_available_ports():
    return serial.tools.list_ports.comports()
