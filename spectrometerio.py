import seabreeze


class spectrometer():
    '''
    Set up the spectrometer
    Return: a spectrometer object
    '''
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
        spec.trigger_mode = 0                               # Setting the trigger mode to normal
        self.states_spectrometer = 1
        spec.integration_time_micros(milliseconds*1000)          # Set integration time for spectrometer
        wavelengths, intensities = spec.spectrum()          # This will return wavelengths and intensities as a 2D array
        self.states_spectrometer = 0
        return wavelengths, intensities                     # Returns array for wavelengths and intensities
    def __init__(self):
        self.states_spectrometer = 0
