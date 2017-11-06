# Standard Libraries
import time
import math

# Major Libraries
import numpy as np

# Enthought library imports
from traits.api import HasTraits, Str, Int, Array, Enum, Float, Instance, Tuple

from ..instrument.api import NI6259


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


def generate_piezo_voltage(min_volt, max_volt, scan_rate, pixels, waveform="Triangular"):
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


def averageArray(input_array, averaging_points):
    if type(input_array) != np.ndarray:
        print "Input array must be numpy array type!"
    else:
        input_array_length = input_array.size
        output_array_length = input_array_length // averaging_points
        output_array = np.zeros(output_array_length, dtype=np.float64)
        for j in range(output_array_length):
            output_array[j] = np.average(input_array[averaging_points*j:averaging_points*(j+1):1])
        return output_array


AO_PORTS = range(4)
AI_PORTS = range(24)

class ScanController(HasTraits):
    """ Controls voltages to be supplied scanners
    """
    daq_board = Instance(NI6259)
    x_axis_index = Enum(AO_PORTS)
    y_axis_index = Enum(AO_PORTS)
    scan_rate = Float(0.1)
    x_scan_range = Tuple((0, 2))
    y_scan_range = Tuple((0, 2))
    pixels = Int(256)
    output_smoothing_ratio = 100
    input_averaging_pts = 100


    def __init__(self, device_name, x_axis_index=0, y_axis_index=1):
        self.daq_board = NI6259(device_name)
        self.x_axis_index = x_axis_index
        self.y_axis_index = y_axis_index

    def sync_scan_read_1d(self):
        samp_time = 1.0 / self.scan_rate
        output_samples = self.pixels * self.output_smoothing_ratio * 2  # 2 for trace and retrace
        input_samples = self.pixels * self.input_averaging_pts * 2      # 2 for trace and retrace
        ao_data = generate_piezo_voltage(self.x_scan_range[0], self.x_scan_range[1], self.scan_rate, output_samples / 2)
        output_samp_rate = (output_samples) / samp_time
        input_samp_rate = (input_samples) / samp_time
        t_data, ai_data = self.daq_board.sync_aoai(self.x_axis_index, 1, ao_data, samp_time, output_samp_rate, input_samp_rate)
        # ai_data_avg = averageArray(ai_data, self.input_averaging_pts)
        ai_data_avg = np.mean(ai_data.reshape(-1, self.input_averaging_pts), axis=1)
        return ai_data_avg

    def sync_scan_read_2d(self):
        slow_axis_squence = np.linspace(self.y_scan_range[0], self.y_scan_range[1], self.pixels)
        image_data = np.zeros((self.pixels, self.pixels))
        for i in range(self.pixels):
            self.daq_board.set_ao(self.y_axis_index, slow_axis_squence[i])
            ai = self.sync_scan_read_1d()
            image_data[i] = ai[:self.pixels]
        return image_data


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    test = ScanController('NI6259')
    test.scan_rate = 0.4
    test.pixels = 64
    # ao_data, ai_data = test.sync_scan_read_1d()
    # plt.plot(ao_data, 'b-')
    # plt.plot(ai_data, 'r-')
    # plt.show()
    # print ao_data[-10:-1], ai_data[-10:-1]
    image = test.sync_scan_read_2d()
    plt.matshow(image)
    plt.show()
