import serial
import serial.tools.list_ports
import time
import threading as thread


class Laser:
    def __init__(self, pulseMode = 0, repRate = 10, burstCount = 10000, diodeCurrent = .1, energyMode = 0, pulseWidth = 10, diodeTrigger = 0):
        self.__ser = serial.Serial()
        self.pulseMode = pulseMode # NOTE: Pulse mode 0 = continuous is actually implemented as 2 = burst mode in this code.
        self.repRate = repRate
        self.burstCount = burstCount
        self.diodeCurrent = diodeCurrent
        self.energyMode = energyMode
        self.pulseWidth = pulseWidth
        self.diodeTrigger = diodeTrigger
        self.burstDuration = burstCount/repRate


        self.__kicker_control = False  # False = off, True = On. Controls kicker for shots longer than 2 seconds
        self.__startup = True
        self.__threads = []
        self.__lock = thread.Lock()
        self.update_settings()

    def editConstants(self, pulseMode = 0, repRate = 10, burstCount = 10000, diodeCurrent = .1, energyMode = 0, pulseWidth = 10,  diodeTrigger = 0):
        """
        Update the laser settings

        Parameters
        ----------
        pulseMode : int
            0 = continuous (actually implemented as burst mode), 1 = single shot, 2 = burst mode in this code.
        repRate : float
            0 = Rate of laser firing in Hz (1 to 30)
        burstCount : int
            number of shots to fire (if pulse mode is 0 or 2)
        diodeCurrent : float
            Current to diode (see laser ATP spec sheet which comes with the laser for  optimal settings)
        energyMode : int
            0 = manual mode, 1 = low power, 2 = high power
        pulseWidth : float
            sets the diode pulse width (see laser ATP spec sheet which comes with laser for optimal settigns)
        diodeTrigger : int
            0 = internal, 1 = external
        """
        self.pulseMode = pulseMode
        self.repRate = repRate
        self.burstCount = burstCount
        self.diodeCurrent = diodeCurrent
        self.energyMode = energyMode
        self.pulseWidth = pulseWidth
        self.diodeTrigger = diodeTrigger
        self.burstDuration = burstCount/repRate
        self.update_settings()

    def __kicker(self):  # queries for status every second in order to kick the laser's WDT on shots >= 2s
        """Queries for status every second in order to kick the laser's WDT on shots >= 2s"""
        while True:
            if self.__kicker_control:
                self.__ser.write(b';LA:SS?<CR>')
            time.sleep(1)

    def __send_command(self, cmd):
        """
        Sends command to laser

        Parameters
        ----------
        cmd : bytes
            This contains the byte signature of the command to be sent
        """
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
        """
        Sets up connection between flight computer and laser

        Parameters
        ----------
        port_number : int
            This is the port number for the laser

        baud_rate : int
            Bits per second on serial connection

        timeout : int
            A buffer for if connection is not established

        """
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

    # Added: changed lock structure
    def fire_laser(self):
        """
            Sends commands to laser to have it fire
        """
        with self.__lock:
            self.__send_command(b';LA:FL 1<CR>')
            self.__send_command(b';LA:SS?<CR>')
            response = self.__ser.readline()

        if response != b'3075<CR>':
            with self.__lock:
                self.__send_command(b';LA:FL 0<CR>')  # aborts if laser fails to fire
            raise RuntimeError('Laser Failed to Fire')
        else:
            if self.burstDuration >= 2:
                self.__kicker_control = True
            time.sleep(self.burstDuration)
            with self.__lock:
                self.__send_command(b';LA:FL 0<CR>')

    def get_status(self):
        """
        Obtains the status of the laser
        Returns
        _______
        status : bytes
            Returns the int value of the status of the laser status in bytes string
                (Sum of 2^13 = High power mode; 2^12 = Low power mode, 2^11 = Ready to fire, 2^10 = Ready to enable
                2^9 = Power failure, 2^8 = Electrical over temp, 2^7 = Resonator over temp, 2^6 = External interlock,
                2^3 = diode external trigger, 2^1 = laser active, 2^0 = laser enabled)
        """
        with self.__lock:
            self.__send_command(b';LA:SS?<CR>')
            return self.__ser.read()

    def check_armed(self):
        """
        Checks if the laser is armed
        Returns
        _______
        armed : boolean
            the lasr is armed
        """
        with self.__lock:
            self.__send_command(b';LA:EN?<CR>')
            # Added: new code
            serial_read = self.__ser.read()[:-4]
            if serial_read == b"0":
                return False
            elif serial_read == b"1":
                return True
            return serial_read

    # Added: FET temperature
    def fet_temp_check(self):
        """
        Checks the FET temperature the laser

        Returns
        _______
        fet : bytes
            Returns the float value of the FET temperature in bytes string.
        """
        with self.__lock:
            self.__send_command(b';LA:FT?<CR>')
            serial_read = self.__ser.read()
            return serial_read[:-4]

    # Added: Resonator temperature
    def resonator_temp_check(self):
        """
        Checks the resonator temperature the laser

        Returns
        _______
        resonator_temp : bytes
            Returns the float value of the resonator temperature in bytes string.
        """
        with self.__lock:
            self.__send_command(b';LA:TR?<CR>')
            serial_read = self.__ser.read()
            return serial_read[:-4]

    # Added: FET voltage
    def fet_voltage_check(self):
        """
        Checks the FET voltage of the laser

        Returns
        _______
        fet_voltage : bytes
            Returns the float value of the FET voltage in bytes string.
        """
        with self.__lock:
            self.__send_command(b';LA:FV?<CR>')
            serial_read = self.__ser.read()
            return serial_read[:-4]

    def diode_current_check(self):
        """
        Checks current to diode of the laser

        Returns
        -------
        diode_current : bytes
            Returns the float value of the diode current in bytes string.
        """
        with self.__lock:
            self.__send_command(b';LA:IM?<CR>')
            serial_read = self.__ser.read()
            return serial_read[:-4]

    # Added: emergency stop
    def emergency_stop(self):
        """Immediately sends command to laser to stop firing (no lock)"""
        self.__send_command(b';LA:FL 0<CR>')

    def arm(self):
        """Sends command to laser to arm"""
        with self.__lock:
            self.__send_command(b';LA:EN 1<CR>')

    def disarm(self):
        """Sends command to laser to disarm"""
        with self.__lock:
            self.__send_command(b';LA:EN 0<CR>')

    def update_settings(self):
        # cmd format, ignore brackets => ;[Address]:[Command String][Parameters]<CR>
        """Updates laser settings"""
        cmd_strings = list()
        cmd_strings.append(';LA:PM ' + str(self.pulseMode) + '<CR>')
        cmd_strings.append(';LA:RR ' + str(self.repRate) + '<CR>')
        cmd_strings.append(';LA:BC ' + str(self.pulseMode) + '<CR>')
        cmd_strings.append(';LA:DC ' + str(self.diodeCurrent) + '<CR>')
        cmd_strings.append(';LA:EM ' + str(self.energyMode) + '<CR>')
        cmd_strings.append(';LA:PM ' + str(self.pulseMode) + '<CR>')
        cmd_strings.append(';LA:DW ' + str(self.pulseWidth) + '<CR>')
        cmd_strings.append(';LA:DT ' + str(self.pulseMode) + '<CR>')

        with self.__lock:
            for i in cmd_strings:
                self.__send_command(i.encode('latin-1'))


def list_available_ports():
    return serial.tools.list_ports.comports()
