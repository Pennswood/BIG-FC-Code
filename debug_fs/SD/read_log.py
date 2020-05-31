import time
import math
import glob
from pathlib import Path
from binascii import hexlify
log_directory_path = Path.cwd() / "logs/"
STATUS_SIZE = 75
def get_log_files():
    l = sorted(log_directory_path.glob("*.statlog"), reverse=True)
    if len(l) == 0:
        return None
    return l
for log_file in get_log_files():
    with open(log_file, "br") as f:
        data = f.read(4)

        while data:
            output = "Time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int.from_bytes(data, "big")))
            data = f.read(1)
            if data == b"\x20": #Off
                output = output + "\nLaser status: off"
            elif data == b"\x21": #warming up
                output = output + "\nLaser status: warming up"
            elif data == b"\x22": #warmed up
                output = output + "\nLaser status: warmed up"
            elif data == b"\x23": #arming
                output = output + "\nLaser status: arming"
            elif data == b"\x24": #armed
                output = output + "\nLaser status: armed"
            elif data == b"\x25": #Firing
                output = output + "\nLaser status: firing"
            data = f.read(1)
            if data == b"\01": #stand-by
                output = output + "\tSpectrometer status: standing by"
            elif data == b"\x02": #integrating
                output = output + "\tSpectrometer status: integrating"
            elif data == b"\xFC": #disconnected
                output = output + "\tSpectrometer status: disconnected"
            output = output + "\n"
            for i in range(8):
                data = f.read(7) #ASCII-encoded 7 bye float
                output = output + "Thermistor "+str(i)+": "+str(bytearray.fromhex(hexlify(data).decode()).decode())+"\t"
            output = output + "\n"
            for i in range(3):
                data = f.read(3) #unsigned etched foil data
                output = output + "Etched foil "+str(i)+": "+str(int.from_bytes(data, "big", signed=False))+"\t"
            output = output + "\nErrors: "
            data = f.read(3)
            decimal_error = int.from_bytes(data, "big", signed=False)
            counter = 0
            while decimal_error >= 1:
                bin = decimal_error % 2
                if bin == 1 and counter == 0:
                    output = output + "LSE Laser setup error\n"
                if bin == 1 and counter == 1:
                    output = output + "FLF Fire laser failed\n"
                if bin == 1 and counter == 2:
                    output = output + "ALF Arm laser failed \n"
                if bin == 1 and counter == 3:
                    output = output + "DSL Available data storage low\n"
                if bin == 1 and counter == 4:
                    output = output + "EDD External data storage is disconnected\n"
                if bin == 1 and counter == 5:
                    output = output + "TO8 Thermistor 8 is offline/non-operational\n"
                if bin == 1 and counter == 6:
                    output = output + "TO7 Thermistor 7 is offline/non-operational\n"
                if bin == 1 and counter == 7:
                    output = output + "TO6 Thermistor 6 is offline/non-operational\n"
                if bin == 1 and counter == 8:
                    output = output + "TO5 Thermistor 5 is offline/non-operational\n"
                if bin == 1 and counter == 9:
                    output = output + "TO5 Thermistor 4 is offline/non-operational\n"
                if bin == 1 and counter == 10:
                    output = output + "TO5 Thermistor 3 is offline/non-operational\n"
                if bin == 1 and counter == 11:
                    output = output + "TO5 Thermistor 2 is offline/non-operational\n"
                if bin == 1 and counter == 12:
                    output = output + "TO5 Thermistor 1 is offline/non-operational\n"
                if bin == 1 and counter == 13:
                    output = output + "TO5 Thermistor 0 is offline/non-operational\n"
                if bin == 1 and counter == 14:
                    output = output + "TIM Payload temperature imbalance\n"
                if bin == 1 and counter == 15:
                    output = output + "TLL Payload temperature low\n"
                if bin == 1 and counter == 16:
                    output = output + "THH Payload temperature high\n"
                if bin == 1 and counter == 17:
                    output = output + "TDD Thermal system disconnected\n"
                if bin == 1 and counter == 18:
                    output = output + "SDD Spectrometer disconnected\n"
                if bin == 1 and counter == 19:
                    output = output + "LDD Laser disconnected\n"
                if bin == 1 and counter == 20:
                    output = output + "ECD Excessive current draw\n"

                counter = counter + 1
                decimal_error = math.floor(decimal_error / 2)
            output = output +"\n"
            data = f.read(1)
            if data == b'\00':
                output = output + "\nLog reason: regular interval log"
            elif data == b'\01':
                output = output + "\nLog reason: rover command"
            elif data == b'\02':
                output = output + "\nLog reason: error detected"
            elif data == b'\03':
                output = output + "\nLog reason: error resolved"
            output = output + "\n_______________________"
            print(output)
            data = f.read(4)