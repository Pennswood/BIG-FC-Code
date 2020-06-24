import numpy as np
import pandas as pd
import random

random.seed(1337)


def generate_dummy_spectra(central_spectra=(500, 730, 380), width=100, bins=1E4, optical_range=(300, 1064)):
    """
    Generates dummy spectra for debugging purposes. Outputs tuple of arrays, index 0 holds the wavelength and index 1
    holds the intensity value. Useful when no spectrometers is present.
    
    Parameters
    ----------
    central_spectra : list
        Integer list of wavelengths to center on
    width : int
        Width of individual line
    bins : int
        Number of samples
    optical_range : tuple
        Range of values to be generated
    
    Returns
    -------
    tuple
        Ruple of arrays. index 0 holds wavelengths, index 1 holds intensity data
    """

    wavelengths = []
    intensities = []
    step = abs(optical_range[1] - optical_range[0])/bins
    # generates wavelength value at increments of range/bins
    for i in range(int(bins)):
        wavelengths.append(optical_range[0] + (i * step))
    for i in wavelengths:
        val = 0
        for j in central_spectra:
            if (j - width/2) <= i <= (j + width/2):
                if (j - width/2) <= i:
                    try:
                        val = 1000/(float(j - i) ** 2)
                    except ZeroDivisionError:
                        val = 1000 / (float(j - i + 0.02) ** 2)
                elif i <= (j + width/2):
                    try:
                        val = 1000/(int(j - i) ** 2)
                    except ZeroDivisionError:
                        val = 1000 / (float(j - i + 0.02) ** 2)
        intensities.append(val)
    spec_data = np.asarray([wavelengths, intensities]).transpose()
    output_frame = pd.DataFrame(data=spec_data, columns=['Wavelength [nm]', 'Intensity'])
    return output_frame

class dummy_laser():
    def receive_command(self,cmd):
        if not cmd[-4:] == "<CR>": #code not complete
            self.cmd = cmd
            return
        if cmd[:3] == ";LA": # new command coming in
            self.cmd = ""
        # code is completed
        cmd = self.cmd + cmd
        self.cmd = ""
        cmd = cmd[3:][:-4]


