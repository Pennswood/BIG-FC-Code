import time
import math
import glob
from pathlib import Path
from binascii import hexlify

# Grab the # of thermisters and heaters from the tlc.py file
from tlc import DUTY_CYCLE_COUNT, THERMISTER_COUNT

log_directory_path = Path.cwd() / "debug_fs" / "SD" / "logs/"

STATUS_SIZE = 75

# Calculate size of status log entry: timestamp (4), thermisters (7 bytes each), heaters (1 byte each), laser status (1 byte), spectrometer status (1 byte), error flags (3 bytes), previous command (1 byte), log reason (1 byte)
STATUS_SIZE = 4 + (7 * THERMISTER_COUNT) + DUTY_CYCLE_COUNT + 1 + 1 + 3 + 1 + 1


def get_log_files():
    l = sorted(log_directory_path.glob("*.statlog"), reverse=True)
    if len(l) == 0:
        return None
    return l


for log_file in get_log_files():
    with log_file.open("rb") as f:
        data = f.read(4)

        while data:
            output = "Time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int.from_bytes(data, "big")))

            data = f.read(1)
            if data == b'\x20':  # Off
                output += "\nLaser status: off"
            elif data == b'\x21':  # warming up
                output += "\nLaser status: warming up"
            elif data == b'\x22':  # warmed up
                output += "\nLaser status: warmed up"
            elif data == b'\x23':  # arming
                output += "\nLaser status: arming"
            elif data == b'\x24':  # armed
                output += "\nLaser status: armed"
            elif data == b'\x25':  # Firing
                output += "\nLaser status: firing"

            data = f.read(1)
            if data == b'\x01':  # stand-by
                output += "\tSpectrometer status: standing by"
            elif data == b'\x02':  # integrating
                output += "\tSpectrometer status: integrating"
            elif data == b'\xFC':  # disconnected
                output += "\tSpectrometer status: disconnected"

            output += "\n"
            print(output)
            for i in range(THERMISTER_COUNT):
                data = f.read(7)  # ASCII-encoded 7 byte float
                s = data.decode("ascii")
                l = int(s[1:4])
                r = int(s[4:7])
                temp_float = float(l) + (0.001 * float(r))
                if s[0] == '-':
                    temp_float = temp_float * -1.0
                output += "Thermistor " + str(i) + ": " + str(temp_float) + "\t"

            output += "\n"
            for i in range(DUTY_CYCLE_COUNT):
                data = f.read(1)  # unsigned etched foil data
                output += "Etched foil " + str(i) + ": " + str(int.from_bytes(data, "big", signed=False)) + "\t"

            output += "\nErrors: \n"
            data = f.read(3)
            decimal_error = int.from_bytes(data, "big", signed=False)
            counter = 0

            while decimal_error >= 1:
                bin = decimal_error % 2
                if bin == 1 and counter == 20:
                    output += "LSE Laser setup error\n"
                if bin == 1 and counter == 19:
                    output += "FLF Fire laser failed\n"
                if bin == 1 and counter == 18:
                    output += "ALF Arm laser failed \n"
                if bin == 1 and counter == 17:
                    output += "DSL Available data storage low\n"
                if bin == 1 and counter == 16:
                    output += "EDD External data storage is disconnected\n"
                if bin == 1 and counter == 15:
                    output += "TO8 Thermistor 8 is offline/non-operational\n"
                if bin == 1 and counter == 14:
                    output += "TO7 Thermistor 7 is offline/non-operational\n"
                if bin == 1 and counter == 13:
                    output += "TO6 Thermistor 6 is offline/non-operational\n"
                if bin == 1 and counter == 12:
                    output += "TO5 Thermistor 5 is offline/non-operational\n"
                if bin == 1 and counter == 11:
                    output += "TO5 Thermistor 4 is offline/non-operational\n"
                if bin == 1 and counter == 10:
                    output += "TO5 Thermistor 3 is offline/non-operational\n"
                if bin == 1 and counter == 9:
                    output += "TO5 Thermistor 2 is offline/non-operational\n"
                if bin == 1 and counter == 8:
                    output += "TO5 Thermistor 1 is offline/non-operational\n"
                if bin == 1 and counter == 7:
                    output += "TO5 Thermistor 0 is offline/non-operational\n"
                if bin == 1 and counter == 6:
                    output += "TIM Payload temperature imbalance\n"
                if bin == 1 and counter == 5:
                    output += "TLL Payload temperature low\n"
                if bin == 1 and counter == 4:
                    output += "THH Payload temperature high\n"
                if bin == 1 and counter == 3:
                    output += "TDD Thermal system disconnected\n"
                if bin == 1 and counter == 2:
                    output += "SDD Spectrometer disconnected\n"
                if bin == 1 and counter == 1:
                    output += "LDD Laser disconnected\n"
                if bin == 1 and counter == 0:
                    output += "ECD Excessive current draw\n"

                counter += 1
                decimal_error = math.floor(decimal_error / 2)

            output += "\n"

            output += "Last command code: " + str(f.read(1))

            data = f.read(1)
            if data == b'\x00':
                output += "\nLog reason: regular interval log"
            elif data == b'\x01':
                output += "\nLog reason: rover command"
            elif data == b'\x02':
                output += "\nLog reason: error detected"
            elif data == b'\x03':
                output += "\nLog reason: error resolved"

            output += "\n_______________________"

            print(output)

            data = f.read(4)
