import mne
import numpy as np
from config import CONFIG
from scipy import integrate
from numpy_ringbuffer import RingBuffer


# Global variables
r = None
f_min = 9.0
f_max = 15.0
window_size_factor_global = 1


def calculate_laplacian(signal):
    """
    Calculate average signal of the j electrodes surrounding the hand knob of
    the motor area
    j = num channels without C3/C4
    :param signal: signals of each channel
    :return: result: calculated average
    :rtype: list[int]
    """

    result = list()
    for i in range(len(signal[0])):
        average = 0
        for j in range(len(signal)):
            average += signal[j][i]
        average /= len(signal)
        result.append(average)

    return result


def calculate_spatial_filtering(signal_list):
    """
    Subtract the calculated average signal from C3 and C4 to perform the spatial filtering
    :param signal_list: signals of all channels (with C3 at position 0 and C4 at position 1)
    :return: signal_c3a: filtered C3, signal_c4a: C4 signals
    :rtype: list[int], list[int]
    """

    signal_c3a = list()
    signal_c4a = list()
    signal_average = calculate_laplacian(signal_list[2:])
    for i in range(len(signal_list[0])):
        signal_c3a.append(signal_list[0][i] - signal_average[i])
        signal_c4a.append(signal_list[1][i] - signal_average[i])

    return signal_c3a, signal_c4a


def perform_multitaper(signal, jobs=-1):
    """
    Performs multitaper function to convert all signals from time into frequency domain
    :param signal: all signals from a channel (should be filtered)
    :param jobs: number of jobs to run in parallel (-1 = num of available CPU cores)
    :return: psd_abs: power spectral density (PSD) of the signal
    :rtype: np.abs(), time()
             freqs: the corresponding frequencies
    """

    array = np.array(signal)
    _bandwidth = f_max - f_min if f_max - f_min > 0 else 1
    psds, freqs = mne.time_frequency.psd_array_multitaper(array, sfreq=128, n_jobs=jobs, bandwidth=_bandwidth,
                                                          fmin=f_min, fmax=f_max)
    psds_abs = np.abs(psds)

    return psds_abs, freqs


def perform_rfft(signal):
    """
    See: https://klyshko.github.io/teaching/2019-02-22-teaching
    Performs fft function to convert all signals from time into frequency domain
    :param signal: all signals from a channel (should be filtered)
    :return: fft_spectrum_abs: power spectral density (PSD) of the signal freqs: frequency
    :rtype: np.abs(), time()
             freqs: the corresponding frequencies
    """

    fft_spectrum = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), d=1 / CONFIG.EEG.SAMPLERATE)
    fft_spectrum_abs = np.abs(fft_spectrum)

    return fft_spectrum_abs, freqs


def integrate_psd_values(signal, frequency_list, use_frequency_filter=False):
    """
    Integrates over the calculated PSD values in between the specified frequencies (FMIN, FMAX)
    :param signal: F(C3), F(C4)
    :param frequency_list: list of the included frequencies
    :param use_frequency_filter: FALSE: if frequencies are already filtered (e.g. with multitaper algorithm),
                                 TRUE: use intern filter
    :return: band_power: sum of all PSDs in the given frequency range
    :rtype: float
    """

    psds_in_band_power = list()
    requested_frequency_range = list()

    if use_frequency_filter:
        for i in range(len(frequency_list)):
            if f_max >= frequency_list[i] >= f_min:
                psds_in_band_power.append(signal[i])
                requested_frequency_range.append(frequency_list[i])

    band_power = integrate.simps(psds_in_band_power, requested_frequency_range) if use_frequency_filter else integrate.simps(signal, frequency_list)

    return band_power


def manage_ringbuffer():
    """
    Das ist ein Singleton :)
    amount of samples within 30 seconds = 30s / 1/250Hz
    size of Ringbuffer = samples within 30s / (sliding_window_factor * 50)
    :return: r: Ringbuffer instance
    :rtype: RingBuffer
    """

    global r
    if not r:
        window_size = window_size_factor_global
        r = RingBuffer(capacity=int(7500 / (window_size * 50)), dtype=np.float)
    return r


def perform_algorithm(sliding_window, window_size_factor=1):
    """
    Converts a sliding window into the corresponding horizontal movement
    Contains following steps:
        (1) Spatial filtering
        (2) Spectral analysis
        (3) Band Power calculation
        (4) Derive normalized cursor control signal
    :param sliding_window: A sliding window (SW) with n channels, n must contain C3 and C4
           (SW(t) should be overlapping with SW(t+1))
    :param window_size_factor: n: n*200ms
    :return: normalized_hcon: the normalized value representing horizontal movement
    :rtype: float
    """

    global window_size_factor_global
    window_size_factor_global = window_size_factor

    # 1. Spatial filtering
    signal_c3a, signal_c4a = calculate_spatial_filtering(sliding_window)

    # 2. Spectral analysis
    psds_c3a_f, freq_c3a_f = perform_multitaper(signal_c3a)
    psds_c4a_f, freq_c4a_f = perform_multitaper(signal_c4a)

    # 3. Band Power calculation
    area_c3 = integrate_psd_values(psds_c3a_f, freq_c3a_f)
    area_c4 = integrate_psd_values(psds_c4a_f, freq_c4a_f)

    # 4. Derive cursor control signal
    hcon = area_c4 - area_c3

    # normalize to zero mean and unit variance to derive the cursor control signal
    ringbuffer = manage_ringbuffer()
    ringbuffer.append(hcon)
    values = np.array(ringbuffer)
    mean = np.mean(values)
    standard_deviation = np.std(values)
    normalized_hcon = (hcon - mean) / standard_deviation if standard_deviation else hcon

    return normalized_hcon
