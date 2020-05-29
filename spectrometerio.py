import seabreeze
import sdcardio as sdcard
import subprocess
import time
import oasis_serial

'''
Set up the spectrometer
Return: a spectrometer object
'''
class Spectrometer():
    def setup_spec(self):
        if seabreeze.spectrometers.list_devices():
            spec = seabreeze.spectrometers.Spectrometer.from_first_available()
        else:
            print("No spectrometer listed")
        return spec

    """
    Taking integration time int and spectrometer object as parameters
    """
    def sample(self, milliseconds, spec):
        spec.trigger_mode = 0                                                                   # Setting the trigger mode to normal
        spec.integration_time_micros(milliseconds*1000)                                         # Set integration time for spectrometer
        self.states_spectrometer = 1                                                            # Spectrometer state is set to sampling
        oasis_serial.sendBytes('\x01')                                                          # Sending nominal responce
        try:
            wavelengths, intensities = spec.spectrum()                                          # This will return wavelengths and intensities as a 2D array, this call also begins the sampling
        except:
            return 'An error occured while attempting to sample'                                # Command to sample didn't work properly

        data = wavelengths, intensities                                                         # Saving 2D array to variable data
        if data == []:
            return 'No data entered'                                                            # Error handling for no data collected
        oasis_serial.sendBytes('\x31')                                                          # Code sent to spectrometer signaling sampling has successfully finished
        date = subprocess.run(['date', "'+%m_%d_%Y_%H_%M_%S'"], timeout = 5, stdout=subprocess.PIPE)    # Running date command on terminal
        filename = '{}'.format(date.stdout.decode('utf-8'))                                     # Creates the time stamped spectrometer file name
        seconds = time.time()                                                                   # Returns # of seconds since Jan 1, 1970 (since epoch)
        sdcard.create_spectrometer_file(filename + '.bin', data, seconds)                       # Function call to create spectrometer file
        self.states_spectrometer = 0                                                            # Spectrometer state is now on standby
        return None

    def __init__(self):
        # 0 = standby, 1 = integrating, 2 = disconnected
        self.states_spectrometer = 0
