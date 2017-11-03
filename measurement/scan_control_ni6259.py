# Standard Libraries
import time
import math

# Major Libraries
import numpy as np


def generate_waveform(waveform, time_span, freq, samp_rate, amplitude, phase, offset):
    """
    Generates an array for the waveform specified
    Parameters
    ----------
    waveform : str
        shape of waveform, either "Sin" or "Triangular"
    time_span : float
        total time for output
    freq : float
        frequency of waveform
    samp_rate : int
        sampling rate for output device
    amplitude : float
        output waveform amplitude
    phase : float
        phase angle in pi
    offset : float
        offset for waveform

    Returns
    -------
    numpy.array
        the array containing the waveform specified
    """
    cycles = int(time_span * freq)
    points_per_cycle = int(samp_rate / freq)
    output_data = np.zeros(time_span * samp_rate, dtype=np.float64)
    if waveform == "Sin":
        for i in range(points_per_cycle):
            for j in range(cycles):
                output_data[i + j * points_per_cycle] = amplitude * np.sin(2*np.pi*float(i)/points_per_cycle + phase)
    elif waveform == "Triangular":
        for i in range(points_per_cycle):
            for j in range(cycles):
                phase_i = i + phase / (2 * np.pi) * points_per_cycle
                temp_value = math.floor(float(phase_i) / (0.5 * points_per_cycle) + 0.5)
                output_data[i + j * points_per_cycle] = amplitude * 4.0 / points_per_cycle * (phase_i - 0.5 * points_per_cycle * temp_value) * (-1) ** temp_value
    return output_data + offset


def generate_piezo_voltage(min_volt, max_volt, scan_rate=0.1, pixels=4096, waveform="Triangular"):
    """
    Generates the sequence of voltages to be applied to the piezo for fast axis scanning
    Parameters
    ----------
    min_volt : float
        the minimum of output voltage in Volt
    max_volt : float
        the maximum of output voltage in Volt
    scan_rate : float
        the scan rate (lines / sec)
    pixels : int
        the number of pixels per line
    waveform : str
        the shape of waveform
    Returns
    -------
    numpy.array
        the output voltage sequence in Volt
    """
    offset = 0.5 * (min_volt + max_volt)
    amplitude = max_volt - offset
    time_span = 1.0 / scan_rate
    samp_rate = 2 * pixels * scan_rate
    phase = np.pi * (-0.5)
    return generate_waveform(waveform=waveform, time_span=time_span, freq=scan_rate, samp_rate=samp_rate, amplitude=amplitude, phase=phase, offset=offset)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    outputdata = generate_piezo_voltage(0, 1)
    plt.plot(outputdata)
    plt.show()
    print outputdata[-1], outputdata[-2]