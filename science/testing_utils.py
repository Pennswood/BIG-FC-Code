import numpy as np
import pandas as pd
import random

random.seed(1337)


def generate_dummy_spectra(central_spectra=(500, 730, 380), width=100, bins=1E4, optical_range=(300, 1064)):
    """
    Generates dummy spectra for debugging purposes. Outputs tuple of arrays, index 0 holds the wavelength and index 1
    holds the intensity value. Useful when no spectrometers is present.
    :param central_spectra: integer list of wavelengths to center on
    :param width: width of individual line
    :param bins: number of samples
    :param optical_range: range of values to be generated
    :return: tuple of arrays. index 0 holds wavelengths, index 1 holds intensity data
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
