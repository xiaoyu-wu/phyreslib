# Standard Libraries
import time
import math

# Major Libraries
import numpy as np

# Enthought library imports
from traits.api import HasTraits, Str, Int, Array, Enum, Float, Instance, Tuple, List, on_trait_change

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


def generate_output_voltage(scan_range, scan_rate, pixels, rotation=0, fast_axis='x', waveform='Triangular'):
    """ Generates output voltage sequences to be applied to x & y channels

    Parameters
    ----------
    scan_range: float
        range to scan in volts
    rotation: float
        counterclockwise angle in rad from original x
    fast_axis: x
        choose from x and y

    Returns
    -------
    Tuple of numpy arrays
    """
    if fast_axis == 'x':
        fast_voltages = generate_piezo_voltage(0, scan_range * np.cos(rotation), scan_rate, pixels, waveform=waveform)
        slow_voltages = generate_piezo_voltage(0, scan_range * np.sin(rotation), scan_rate, pixels, waveform=waveform)
    elif fast_axis == 'y':
        slow_voltages = generate_piezo_voltage(0, -scan_range * np.sin(rotation), scan_rate, pixels, waveform=waveform)
        fast_voltages = generate_piezo_voltage(0, scan_range * np.cos(rotation), scan_rate, pixels, waveform=waveform)
    else:
        raise ValueError("Invalid fast axis selection. Must be \"x\" or \"y\"")
        return
    return fast_voltages, slow_voltages


AO_PORTS = range(4)
AI_PORTS = range(24)


class ScanController(HasTraits):
    """ Controls voltages to be supplied scanners
    """
    # Hardware
    daq_board = Instance(NI6259)
    # Hardware config. Output
    x_axis_index = Enum(AO_PORTS)
    y_axis_index = Enum(AO_PORTS)
    # Hardware config. Input
    input_ports = List([])
    # Scan config.
    scan_rate = Float(0.1)
    fast_scan_range = Float(1)
    slow_scan_range = Float(1)
    pixels = Int(256)
    output_smoothing_ratio = 100
    input_averaging_pts = 100
    rotation = Float(0)
    fast_axis = Enum("x", "y")
    start_position = List([0, 0])
    current_position = List([0, 0])

    def __init__(self, device_name, x_axis_index=0, y_axis_index=1):
        super(ScanController, self).__init__()
        self.daq_board = NI6259(device_name)
        self.x_axis_index = x_axis_index
        self.y_axis_index = y_axis_index
        self.fast_axis = "x"
        self.input_ports += [1, 3]


    @on_trait_change('rotation')
    def check_corner_positions(self, object, name, old, new):
        corners = [np.array(self.start_position)]
        if self.fast_axis == 'x':
            fast_add = np.array([self.fast_scan_range * np.cos(self.rotation), self.fast_scan_range * np.sin(self.rotation)])
            slow_add = np.array([- self.slow_scan_range * np.sin(self.rotation), self.slow_scan_range * np.cos(self.rotation)])
        else:
            fast_add = np.array([- self.fast_scan_range * np.sin(self.rotation), self.fast_scan_range * np.cos(self.rotation)])
            slow_add = np.array([self.slow_scan_range * np.cos(self.rotation), self.slow_scan_range * np.sin(self.rotation)])

        corners.append(corners[0] + fast_add)
        corners.append(corners[0] + slow_add)
        corners.append(corners[0] + fast_add + slow_add)

        for corner in corners:
            if corner[0] < 0 or corner[1] < 0:
                print "WARNING! Negative voltage applied to piezo. Reset to previous rotation angle."
                self.rotation = old
                return

    def sync_scan_read_1d(self):
        samp_time = 1.0 / self.scan_rate
        output_samples = self.pixels * self.output_smoothing_ratio * 2  # 2 for trace and retrace
        input_samples = self.pixels * self.input_averaging_pts * 2      # 2 for trace and retrace
        ao_data = generate_piezo_voltage(0, self.fast_scan_range, self.scan_rate, output_samples / 2)
        output_samp_rate = (output_samples) / samp_time
        input_samp_rate = (input_samples) / samp_time
        t_data, ai_data = self.daq_board.sync_aoai(self.x_axis_index, 1, ao_data, samp_time, output_samp_rate, input_samp_rate)
        # averages the input sequence every n points, n = input_averaging_pts
        ai_data_avg = np.mean(ai_data.reshape(-1, self.input_averaging_pts), axis=1)
        return ai_data_avg

    def sync_scan_read_1d_with_rotation(self):
        samp_time = 1.0 / self.scan_rate
        output_samples = self.pixels * self.output_smoothing_ratio * 2  # 2 for trace and retrace
        input_samples = self.pixels * self.input_averaging_pts * 2      # 2 for trace and retrace
        fast_ao_data, slow_ao_data = generate_output_voltage(self.fast_scan_range, self.scan_rate,
                                                             output_samples / 2, rotation=self.rotation,
                                                             fast_axis=self.fast_axis)
        if self.fast_axis == 'x':
            fast_ao_data += self.current_position[0]
            fast_axis_index = self.x_axis_index
            slow_ao_data += self.current_position[1]
            slow_axis_index = self.y_axis_index
        else:
            fast_ao_data += self.current_position[1]
            fast_axis_index = self.y_axis_index
            slow_ao_data += self.current_position[0]
            slow_axis_index = self.x_axis_index
        output_samp_rate = output_samples / samp_time
        input_samp_rate = input_samples / samp_time
        ai_data = self.daq_board.sync_multi_channel_aoai([fast_axis_index, slow_axis_index], self.input_ports, [fast_ao_data, slow_ao_data], samp_time, output_samp_rate, input_samp_rate)
        ai_data_avg = np.zeros((len(self.input_ports), self.pixels * 2))
        for i in range(len(self.input_ports)):
            ai_data_avg[i] = np.mean(ai_data[i].reshape(-1, self.input_averaging_pts), axis=1)
        return ai_data_avg

    def sync_scan_read_2d(self):
        slow_axis_sequence = np.linspace(0, self.slow_scan_range, self.pixels)
        image_data = np.zeros((self.pixels, 2 * self.pixels))

        for i in range(self.pixels):
            self.daq_board.set_ao(self.y_axis_index, slow_axis_sequence[i])
            ai = self.sync_scan_read_1d()
            image_data[i] = ai[:]
        image_data_trace = image_data[:, :self.pixels]
        image_data_retrace = image_data[:, self.pixels:]
        return image_data_trace, image_data_retrace

    def sync_scan_read_2d_with_rotation(self):
        if self.fast_axis == 'x':
            destination = (-np.sin(self.rotation) * self.slow_scan_range, np.cos(self.rotation) * self.slow_scan_range)
        else:
            destination = (np.cos(self.rotation) * self.slow_scan_range, np.sin(self.rotation) * self.slow_scan_range)
        x_sequence = np.linspace(self.current_position[0], destination[0], self.pixels)
        y_sequence = np.linspace(self.current_position[1], destination[1], self.pixels)
        images = np.zeros((len(self.input_ports), self.pixels, 2*self.pixels))

        for i in range(self.pixels):
            self.daq_board.set_ao(self.x_axis_index, x_sequence[i])
            self.daq_board.set_ao(self.y_axis_index, y_sequence[i])
            self.current_position[0] = x_sequence[i]
            self.current_position[1] = y_sequence[i]
            ai = self.sync_scan_read_1d_with_rotation()
            images[:, i, :] = ai
        images_trace = images[:, :, :self.pixels]
        images_retrace = images[:, :, self.pixels:]
        return images_trace, images_retrace


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    test = ScanController('NI6259')
    test.scan_rate = 1
    test.pixels = 16
    test.rotation = np.pi / 6
    print test.rotation
    test.fast_axis = 'x'
    test.slow_scan_range = 1
    test.output_smoothing_ratio = 100
    test.input_averaging_pts = 100
    # ao_data, ai_data = test.sync_scan_read_1d()
    # plt.plot(ao_data, 'b-')
    # plt.plot(ai_data, 'r-')
    # plt.show()
    # print ao_data[-10:-1], ai_data[-10:-1]
    images_t, images_r = test.sync_scan_read_2d_with_rotation()
    plt.subplot(221)
    plt.imshow(images_t[0])
    plt.subplot(222)
    plt.imshow(images_r[0])
    plt.subplot(223)
    plt.imshow(images_t[1])
    plt.subplot(224)
    plt.imshow(images_r[1])
    plt.show()