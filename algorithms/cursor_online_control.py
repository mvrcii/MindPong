import enum
import scipy.integrate
import mne
import numpy as np
from numpy import linspace
from scipy import signal
from numpy_ringbuffer import RingBuffer
from spectrum import arburg, arma2psd

# Global variables
R = None
FMIN = 8.0
FMAX = 12.0
# WINDOW_OFFSET = 0.05
# WINDOW_SIZE = 1
THRESHOLD = 1
SAMPLING_FREQ = 125
WEIGHT = 2


class PSD_METHOD(enum.Enum):
    fft = 1
    multitaper = 2
    burg = 3
    periodogram = 4


def norm_data(in_data):
    # normalize data
    mean = np.mean(in_data)
    std = np.std(in_data)
    out_data = in_data - mean
    out_data = out_data / std
    return out_data


def mute_outliers(samples: np.ndarray):
    mean = np.mean(samples)
    std = np.std(samples)
    x = 4.0
    output = samples
    for i in range(len(samples)):
        if samples[i] > mean + x * std:
            output[i] = mean + x * std
        if samples[i] < mean - x * std:
            output[i] = mean - x * std

    return output


def calculate_laplacian(samples: np.ndarray):
    """
    Calculate average samples of the j electrodes surrounding the hand knob of
    the motor area
    j = num channels without C3/C4
    :param samples: samples of each channel
    :return: calculated average
    """
    result = list()
    for i in range(len(samples[0])):
        average = 0
        for j in range(len(samples)):
            average += samples[j][i]
        average /= len(samples)
        result.append(average)

    result = np.asarray(result)
    return result


def split_normalization_area(samples_list: np.ndarray, used_ch_names: list):
    """
    description...
    """
    channels_around_c3 = list()
    channels_around_c4 = list()

    for i in range(len(used_ch_names)):
        c = used_ch_names[i][-1]

        if c.isnumeric():
            if int(c) % 2 == 0:
                channels_around_c4.append(samples_list[i])
            else:
                channels_around_c3.append(samples_list[i])
        else:
            channels_around_c3.append(samples_list[i])
            channels_around_c4.append(samples_list[i])

    channels_around_c3 = np.asarray(channels_around_c3)
    channels_around_c4 = np.asarray(channels_around_c4)
    return channels_around_c3, channels_around_c4


def calculate_spatial_filtering(samples_list: np.ndarray, used_ch_names: list):
    """
    Subtract the calculated average samples from C3 and C4 to perform the spatial filtering
    :param samples_list: samples of all channels (with C3 at position 0 and C4 at position 1)
    :return: filtered C3, C4 samples
    """
    samples_c3a = list()
    samples_c4a = list()
    samples_c3 = mute_outliers(samples_list[0][:])
    samples_c4 = mute_outliers(samples_list[1][:])
    # splits the channels into c3 and c4 related channels
    split_channels = split_normalization_area(samples_list[2:], used_ch_names[2:])

    # calculate the average for the c3 and c4 related channels
    samples_average_c3 = calculate_laplacian(split_channels[0][:])
    samples_average_c4 = calculate_laplacian(split_channels[1][:])
    samples_average_c3 = mute_outliers(samples_average_c3)
    samples_average_c4 = mute_outliers(samples_average_c4)

    for i in range(len(samples_list[0])):
        # samples_c3a.append(samples_list[0][i] - samples_average_c3[i])
        # samples_c4a.append(samples_list[1][i] - samples_average_c4[i])
        samples_c3a.append(samples_c3[i] - samples_average_c3[i])
        samples_c4a.append(samples_c4[i] - samples_average_c4[i])

    samples_c3a = np.asarray(samples_c3a)
    samples_c4a = np.asarray(samples_c4a)
    return samples_c3a, samples_c4a


def perform_multitaper(samples: np.ndarray, jobs=-1):
    """
    Performs multitaper function to convert all samples from time into frequency domain
    :param samples: all samples from a channel (should be filtered)
    :param jobs: number of jobs to run in parallel (-1 = num of available CPU cores)
    :return: psd_abs: power spectral density (PSD) of the samples
             freqs: the corresponding frequencies
    """
    _bandwidth = FMAX - FMIN if FMAX - FMIN > 0 else 1
    psds, freqs = mne.time_frequency.psd_array_multitaper(samples, sfreq=SAMPLING_FREQ, n_jobs=jobs, bandwidth=_bandwidth, fmin=FMIN, fmax=FMAX, verbose=False)
    psds_abs = np.abs(psds)

    return psds_abs, freqs


def perform_periodogram(samples: np.ndarray):
    return signal.periodogram(samples, SAMPLING_FREQ)


def perform_rfft(samples: np.ndarray):
    """
    See: https://klyshko.github.io/teaching/2019-02-22-teaching
    Performs fft function to convert all samples from time into frequency domain
    :param samples: all samples from a channel (should be filtered)
    :return: fft_spectrum_abs: power spectral density (PSD) of the samples
             freqs: the corresponding frequencies
    """
    fft_spectrum = np.fft.rfft(samples)
    freqs = np.fft.rfftfreq(len(samples), d=1 / SAMPLING_FREQ)
    fft_spectrum_abs = np.abs(fft_spectrum)

    return fft_spectrum_abs, freqs


def perform_burg(sample: np.array):
    """
    recommended for small window sizes
    """
    AR, P, k = arburg(sample, 10)
    PSD = arma2psd(AR)
    space = linspace(0, 50, PSD.size)

    # caution! bandpassfilter with 50Hz required
    return PSD, space


def integrate_psd_values(samples: np.ndarray, frequency_list: np.ndarray, used_filter):
    """
    Integrates over the calculated PSD values in between the specified frequencies (FMIN, FMAX)
    :param samples: F(C3), F(C4)
    :param frequency_list: list of the included frequencies
    :return: sum of all PSDs in the given frequency range
    """

    psds_in_band_power = list()
    requested_frequency_range = list()

    if used_filter == PSD_METHOD.fft or used_filter == PSD_METHOD.burg or used_filter == PSD_METHOD.periodogram:
        for i in range(len(frequency_list)):
            if FMAX >= frequency_list[i] >= FMIN:
                psds_in_band_power.append(samples[i])
                requested_frequency_range.append(frequency_list[i])

        band_power = scipy.integrate.trapz(psds_in_band_power, requested_frequency_range) if len(requested_frequency_range) > 0 else 0
    else:
        band_power = scipy.integrate.trapz(samples, frequency_list)

    # band_power = integrate.simps(psds_in_band_power, requested_frequency_range) if use_frequency_filter else integrate.simps(samples, frequency_list)

    return band_power


def manage_ringbuffer(window_size, offset_in_percentage:float):
    """
    Das ist ein Singleton :)
    amount of samples within 30 seconds = 30s / 1/250Hz
    size of Ringbuffer = samples within 30s / (sliding_window_factor * 50)
    :return: Ringbuffer instance
    """
    global R
    if not R:
        offset = window_size/(offset_in_percentage*100.0)
        R = RingBuffer(capacity=int(((30-window_size) / offset)+1), dtype=np.float)
    return R


def perform_algorithm(sliding_window, used_ch_names, sample_rate, queue_hcon=None, queue_c3=None, queue_c4=None, offset_in_percentage=0.2):
    """
    Converts a sliding window into the corresponding horizontal movement
    Contains following steps:
        (1) Spatial filtering
        (2) Spectral analysis
        (3) Band Power calculation
        (4) Derive normalized cursor control samples
    :param sliding_window: A sliding window (SW) with n channels, n must contain C3 and C4
           (SW(t) should be overlapping with SW(t+1))
    :param window_size_factor: n: n*200ms
    :return: the normalized value representing horizontal movement
    """

    used_method = PSD_METHOD.multitaper

    # 0. mute outliers
    for i in range(len(sliding_window)):
        sliding_window[i] = norm_data(sliding_window[i])

    global SAMPLING_FREQ
    SAMPLING_FREQ = sample_rate

    # 1. Spatial filtering
    samples_c3a, samples_c4a = calculate_spatial_filtering(sliding_window, used_ch_names)

    # 2. Spectral analysis
    if used_method == PSD_METHOD.fft:
        psd_c3a, f_c3a = perform_rfft(samples_c3a)
        psd_c4a, f_c4a = perform_rfft(samples_c4a)
    elif used_method == PSD_METHOD.periodogram:
        f_c3a, psd_c3a = perform_periodogram(samples_c3a)
        f_c4a, psd_c4a = perform_periodogram(samples_c4a)
    elif  used_method == PSD_METHOD.burg:
        f_c3a, psd_c3a = perform_burg(samples_c3a)
        f_c4a, psd_c4a = perform_burg(samples_c4a)
    elif used_method == PSD_METHOD.multitaper:
        psd_c3a, f_c3a = perform_multitaper(samples_c3a)
        psd_c4a, f_c4a = perform_multitaper(samples_c4a)
    else:
        raise NotImplementedError(f'The specified method {used_method} is NOT supported!')

    # 3. Band Power calculation
    area_c3 = integrate_psd_values(psd_c3a, f_c3a, used_method)
    area_c4 = integrate_psd_values(psd_c4a, f_c4a, used_method)

    # 4. Derive cursor control samples
    hcon = (area_c4*WEIGHT) - area_c3

    # normalize to zero mean and unit variance to derive the cursor control samples
    ringbuffer = manage_ringbuffer((len(sliding_window[0]) + 1)/sample_rate, offset_in_percentage)
    if not ringbuffer.is_full:
        ringbuffer.append(hcon)

    values = np.array(ringbuffer)
    mean = np.mean(values)
    standard_deviation = np.std(values)
    normalized_hcon = (hcon - mean) / standard_deviation if standard_deviation else 0

    global THRESHOLD
    threshold = THRESHOLD

    # converts the returned hcon to the corresponding label
    if normalized_hcon > threshold-0.2:     # left
        calculated_label = 0
    elif normalized_hcon < -threshold:  # right
        calculated_label = 1
    else:
        calculated_label = -1

    try:
        if queue_hcon:
            queue_hcon.put(0)
        if queue_c3:
            queue_c3.put(area_c3)
        if queue_c4:
            queue_c4.put(area_c4)
    except:
        print('Fehler: hcon kann nicht reingeldaden werden')

    return calculated_label
