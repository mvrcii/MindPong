import enum
import scipy.integrate
import mne
import numpy as np
from numpy import linspace
from scipy import signal
from numpy_ringbuffer import RingBuffer
# from spectrum import arburg, arma2psd
from scripts.utils.event_listener import post_event
from scripts.data.acquisition.read_data import QueueManager
import scripts.config as config

# method for psd estimation
class PSD_METHOD(enum.Enum):
    fft = 1
    multitaper = 2
    periodogram = 3
    burg = 4


# Global variables
ringbuffer_hcon = None
F_MIN: float
F_MAX: float
SAMPLING_FREQ: int
USED_METHOD = PSD_METHOD.multitaper


def standardise_data(in_data):
    # standardises data
    # Benefit of standardisation rather than normalisation, as standardisation is much more robust against outliers.
    mean = np.mean(in_data)
    std = np.std(in_data)
    out_data = in_data - mean
    out_data = out_data / std
    return out_data


def mute_outliers(samples: np.ndarray):
    # Outliers of the signal that are smaller or larger than x times the standard deviation,
    # starting from the medium of the signal, are cut off.
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


def split_laplacian_areas(samples_list: np.ndarray, used_ch_names: list):
    """
    Divide the channel into the corresponding areas for c3 and c4.
    Channels with an even number in the name belong to C4, and with an odd number to C3.
    :param samples_list:list of the channels
    :param used_ch_names: list of the channel names associated with the channel
    :return: 2 list containing sorted channels belonging to c3 and c4
    """
    channels_around_c3 = list()
    channels_around_c4 = list()

    for i in range(len(used_ch_names)):
        c = used_ch_names[i][-1]

        # sort into channels belonging to c3 and c4
        if c.isnumeric():
            if int(c) % 2 == 0:
                channels_around_c4.append(samples_list[i])
            else:
                channels_around_c3.append(samples_list[i])
        else:
            channels_around_c3.append(samples_list[i])
            channels_around_c4.append(samples_list[i])

    # convert back to np arrays
    channels_around_c3 = np.asarray(channels_around_c3)
    channels_around_c4 = np.asarray(channels_around_c4)
    return channels_around_c3, channels_around_c4


def calculate_spatial_filtering(samples_list: np.ndarray, used_ch_names: list):
    """
    Subtract the calculated average samples from C3 and C4 to perform the spatial filtering
    :param used_ch_names: associated names of all channels (with C3 at position 0 and C4 at position 1)
    :param samples_list: samples of all channels (with C3 at position 0 and C4 at position 1)
    :return: filtered C3, C4 samples
    """
    samples_c3a = list()
    samples_c4a = list()
    # splits the channels into c3 and c4 related channels
    split_channels = split_laplacian_areas(samples_list[2:], used_ch_names[2:])
    # calculate the average for the c3 and c4 related channels
    samples_average_c3 = calculate_laplacian(split_channels[0][:])
    samples_average_c4 = calculate_laplacian(split_channels[1][:])

    # mute outliers
    samples_c3 = mute_outliers(samples_list[0][:])
    samples_c4 = mute_outliers(samples_list[1][:])
    samples_average_c3 = mute_outliers(samples_average_c3)
    samples_average_c4 = mute_outliers(samples_average_c4)

    for i in range(len(samples_list[0])):
        # samples_c3a.append(samples_list[0][i] - samples_average_c3[i])
        # samples_c4a.append(samples_list[1][i] - samples_average_c4[i])
        samples_c3a.append(samples_c3[i] - samples_average_c3[i])
        samples_c4a.append(samples_c4[i] - samples_average_c4[i])

    # convert back to np arrays
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
    _bandwidth = F_MAX - F_MIN if F_MAX - F_MIN > 0 else 1
    psds, freqs = mne.time_frequency.psd_array_multitaper(samples, sfreq=SAMPLING_FREQ, n_jobs=jobs, bandwidth=_bandwidth, fmin=F_MIN, fmax=F_MAX, verbose=False)
    psds_abs = np.abs(psds)

    return psds_abs, freqs


def perform_periodogram(samples: np.ndarray):
    return signal.periodogram(samples, SAMPLING_FREQ)


def perform_rfft(samples: np.ndarray):
    """
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
    :param sample: all samples from a channel (should be filtered)
    :return: fft_spectrum_abs: power spectral density (PSD) of the samples
             freqs: the corresponding frequencies
    """
    AR, P, k = arburg(sample, 10)
    PSD = arma2psd(AR)
    space = linspace(0, 50, PSD.size)

    # caution! bandpass filter with 50Hz required
    return PSD, space


def integrate_psd_values(samples: np.ndarray, frequency_list: np.ndarray, used_filter):
    """
    Integrates over the calculated PSD values in between the specified frequencies (F_MIN, F_MAX)
    :param used_filter: Set the previously used filter to control integration
    :param samples: F(C3), F(C4)
    :param frequency_list: list of the included frequencies
    :return: sum of all PSDs in the given frequency range
    """

    psds_in_band_power = list()
    requested_frequency_range = list()

    # psd methods whose return values do not automatically contain exclusively the desired frequency range must be modified.
    if used_filter == PSD_METHOD.fft or used_filter == PSD_METHOD.burg or used_filter == PSD_METHOD.periodogram:
        for i in range(len(frequency_list)):
            if F_MAX >= frequency_list[i] >= F_MIN:
                psds_in_band_power.append(samples[i])
                requested_frequency_range.append(frequency_list[i])

        band_power = scipy.integrate.trapz(psds_in_band_power, requested_frequency_range) if len(requested_frequency_range) > 0 else 0
    # only Multitaper returns the already  desired frequency range
    else:
        band_power = scipy.integrate.trapz(samples, frequency_list)

    return band_power


def manage_ringbuffer(window_size, offset_in_percentage: float):
    """
    Das ist ein Singleton :)
    amount of samples within 30 seconds = 30s / 1/250Hz
    size of Ringbuffer = samples within 30s / (sliding_window_factor * 50)
    :return: Ringbuffer instance
    """
    global ringbuffer_hcon
    if not ringbuffer_hcon:
        offset = window_size/(offset_in_percentage*100.0)
        ringbuffer_hcon = RingBuffer(capacity=int(((30 - window_size) / offset) + 1), dtype=np.float)
    return ringbuffer_hcon


def perform_algorithm(sliding_window, used_ch_names, sample_rate, queue_manager: QueueManager, data_mdl, offset_in_percentage=0.2):
    """
    Converts a sliding window into the corresponding horizontal movement
    Contains following steps:
        (1) Spatial filtering
        (2) Spectral analysis
        (3) Band Power calculation
        (4) Derive normalized cursor control samples
    :param data_mdl: reference of datamodel, where constants of cc_algorithm are stored
    :param queue_manager: reference of queue manager to pass data to liveplot in another thread
    :param sample_rate: sample rate of the samples
    :param used_ch_names: name of the used channel from the samples
    :param sliding_window: A sliding window (SW) with n channels, n must contain C3 and C4
           (SW(t) should be overlapping with SW(t+1))
    :param offset_in_percentage: offset between start of new window in percentage
    :return: the normalized value representing horizontal movement
    """

    # 0. mute outliers
    for i in range(len(sliding_window)):
        sliding_window[i] = standardise_data(sliding_window[i])

    global SAMPLING_FREQ, F_MIN, F_MAX
    SAMPLING_FREQ = sample_rate
    F_MIN = data_mdl.f_min
    F_MAX = data_mdl.f_max

    # 1. Spatial filtering
    samples_c3a, samples_c4a = calculate_spatial_filtering(sliding_window, used_ch_names)

    # 2. Spectral analysis
    if USED_METHOD == PSD_METHOD.fft:
        psd_c3a, f_c3a = perform_rfft(samples_c3a)
        psd_c4a, f_c4a = perform_rfft(samples_c4a)
    elif USED_METHOD == PSD_METHOD.periodogram:
        f_c3a, psd_c3a = perform_periodogram(samples_c3a)
        f_c4a, psd_c4a = perform_periodogram(samples_c4a)
    elif  USED_METHOD == PSD_METHOD.burg:
        f_c3a, psd_c3a = perform_burg(samples_c3a)
        f_c4a, psd_c4a = perform_burg(samples_c4a)
    elif USED_METHOD == PSD_METHOD.multitaper:
        psd_c3a, f_c3a = perform_multitaper(samples_c3a)
        psd_c4a, f_c4a = perform_multitaper(samples_c4a)
    else:
        raise NotImplementedError(f'The specified method {USED_METHOD} is NOT supported!')

    # 3. Band Power calculation
    area_c3 = integrate_psd_values(psd_c3a, f_c3a, USED_METHOD)
    area_c4 = integrate_psd_values(psd_c4a, f_c4a, USED_METHOD)

    # 4. derivation of the control signal hcon from integrated PSD values of c3 and c4
    hcon = (area_c4*config.WEIGHT) - area_c3

    ringbuffer = manage_ringbuffer((len(sliding_window[0]) + 1)/sample_rate, offset_in_percentage)
    # Conditional instruction is responsible for writing to the ring buffer only in the first 30 seconds.
    if not ringbuffer.is_full:
        ringbuffer.append(hcon)

    # From the collected previous calculated hcon values from (the last ) 30 seconds,
    # a standard deviation and a mean value are determined.
    # The current hcon is standardised with these values
    values = np.array(ringbuffer)
    mean = np.mean(values)
    standard_deviation = np.std(values)
    standardised_hcon = (hcon - mean) / standard_deviation if standard_deviation else 0

    # converts the returned hcon to the corresponding label
    if standardised_hcon > data_mdl.threshold-0.2:     # left
        calculated_label = 0
        post_event("move_left_direction")
    elif standardised_hcon < -data_mdl.threshold:  # right
        calculated_label = 1
        post_event("move_right_direction")
    else:
        calculated_label = -1

    # only fill queues if the plot gets drawn and queues are not full
    if data_mdl.draw_plot:
        if not queue_manager.queue_hcon.full():
            queue_manager.queue_hcon_stand.put(standardised_hcon)
            queue_manager.queue_hcon.put(hcon)
        if not queue_manager.queue_c3_pow.full() and not queue_manager.queue_c4_pow.full():
            queue_manager.queue_c3_pow.put(area_c3)
            queue_manager.queue_c4_pow.put(area_c4)
        if not queue_manager.queue_clabel.full():
            queue_manager.queue_clabel.put(calculated_label, True)

    return calculated_label
