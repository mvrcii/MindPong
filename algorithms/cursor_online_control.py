import matplotlib.pyplot as plt
import mne
import numpy as np
from config import CONFIG
from scipy import integrate
from numpy_ringbuffer import RingBuffer
from spectrum import pburg

"""
Documentation: Pin mapping
    Cyton board is mapped to the first 8 positions in the list amd the daisy board to the further 8 positions
        Node | Pin | Position
             |     | in list
-------------|-----|----------
Cyton:   C3  |  1  |    0
         C4  |  3  |    2
Daisy:  FC1  |  2  |   10
        FC2  |  3  |   11
        CP1  |  6  |   14
        CP2  |  7  |   15


Structure of 4-dim array from the data loader:
        dim 0: subject
        dim 1: trial
        dim 3: EEG channel
        dim 4: sample

"""

'''
Calculate average signal of the four electrodes surrounding the hand knob of 
the motor area (small laplacian)
'''

# Global variables
r = None


def calculate_small_laplacian(signal):
    counter = 0
    length = len(signal[0])
    result = list()

    while counter < length:
        average = 0
        for i in range(len(signal)):
            average += signal[i][counter]
        average /= len(signal)
        result.append(average)
        counter += 1

    return result


'''
Subtract the calculated average signal from C3 and C4 to perform the spatial filtering
'''


def calculate_spatial_filtering(signal_list):
    signal_c3a = list()
    signal_c4a = list()
    # TODO: ((maybe)) adjust structure of the lists
    signal_average = calculate_small_laplacian(signal_list[2:])

    length = len(signal_list[0])
    counter = 0
    while counter < length:
        signal_c3a.append(signal_list[0][counter] - signal_average[counter])
        signal_c4a.append(signal_list[1][counter] - signal_average[counter])
        counter += 1

    return signal_c3a, signal_c4a


def perform_multitaper(signal, jobs=-1):
    array = np.array(signal)
    psds, freqs = mne.time_frequency.psd_array_multitaper(array, sfreq=128, n_jobs=jobs, bandwidth=6.0, fmin=9.0, fmax=15.0)
    psds_abs = np.abs(psds)
    return psds_abs, freqs


def perform_rfft(signal):
    fft_spectrum = np.fft.rfft(signal)
    freq = np.fft.rfftfreq(len(signal), d=1 / CONFIG.EEG.SAMPLERATE)
    fft_spectrum_abs = np.abs(fft_spectrum)

    return fft_spectrum_abs, freq


def perform_burg(signal):
 #  AR, P, k = arburg(signal, 10, sampling=128)
    pass


def integrate_psd_values(signal, frequency_list):
    # calculate alpha frequency array
    counter = 0
    length = len(frequency_list)
    alpha_band_power = list()
    requested_frequency_range = list()

    # TODO: evaluate if necessary !!!
    while counter < length:
        if 15.0 >= frequency_list[counter] >= 9.0:
            alpha_band_power.append(signal[counter])
            requested_frequency_range.append(frequency_list[counter])
        counter += 1

    # print(f'alpha band power {alpha_band_power}\nfrequency range {requested_frequency_range}')
    uFreq = 0  # upper und lower frequency point
    lFreq = len(alpha_band_power) - 1

    '''integration doesnt work because array doesnt have the same size!!!
        solution: create an alpha-band-power array, that has the which has the 
        corresponding values to array x 
    '''

    # Convenience algo using the trapezoid rule
    # spacing = np.linspace(uFreq, lFreq, integration_steps+1)
    # area = np.trapz(alpha_band_power, requested_frequency_range)        # spacing is only taken into account if x is missing

    # diy trapz with configuable interation steps
    # y_right = alpha_band_power[1:]  # determines which entries in the sum function are offset against each other
    # y_left = alpha_band_power[:-1]  # by creating arrays from [1:n] and from [0:n-1] that way yi+1 & yi are always summed up
    # # trapezoid rule
    # integration_steps = lFreq + 1
    # dx = (lFreq - uFreq) / integration_steps
    # area = (dx / 2) * np.sum(y_right + y_left)
    area = integrate.simps(alpha_band_power, requested_frequency_range)

    return area


def manage_ringbuffer():
    # Das ist ein Singleton :)
    global r
    if not r:
        # TODO: define adjustable capacity of the ringbuffer
        r = RingBuffer(capacity=300, dtype=np.float)

    return r


def perform_algorithm(sliding_window):
    # 1. Spatial Filtering
    signal_c3a, signal_c4a = calculate_spatial_filtering(sliding_window)

    # 2. PSD calculation via FFT
    psds_c3a_f, freq_c3a_f = perform_multitaper(signal_c3a)
    psds_c4a_f, freq_c4a_f = perform_multitaper(signal_c4a)

    # 3. Alpha Band Power calculation
    area_c3 = integrate_psd_values(psds_c3a_f, freq_c3a_f)
    area_c4 = integrate_psd_values(psds_c4a_f, freq_c4a_f)

    # Derive cursor control signals
    hcon = area_c4 - area_c3

    ringbuffer = manage_ringbuffer()
    ringbuffer.append(hcon)
    values = np.array(ringbuffer)
    mean = np.mean(values)
    standard_deviation = np.std(values)
    normalized_hcon = (hcon - mean) / standard_deviation if standard_deviation else hcon

    return normalized_hcon


# def load_values_in_ringbuffer(sliding_window):
#     # 1. Spatial Filtering
#     signal_c3a, signal_c4a = calculate_spatial_filtering(sliding_window)
#
#     # 2. PSD calculation via FFT
#     psds_c3a_f, freq_c3a_f = perform_rfft(signal_c3a)
#     psds_c4a_f, freq_c4a_f = perform_rfft(signal_c4a)
#     psds_c3a_m, freq_c3a_m = perform_multitaper(signal_c3a)
#     psds_c4a_m, freq_c4a_m = perform_multitaper(signal_c4a)
#
#     # 3. Alpha Band Power calculation
#     area_c3_f = integrate_psd_values(psds_c3a_f, freq_c3a_f)
#     area_c3_m = integrate_psd_values(psds_c3a_m, freq_c3a_m)
#     area_c4_m = integrate_psd_values(psds_c4a_m, freq_c4a_m)
#
#     # Derive cursor control signals
#     hcon = area_c4_m - area_c3_m
#     # fig, axs = plt.subplots(2)
#     # axs[0].plot(signal_c3a, 'r')
#     # axs[0].plot(psds_c3a_f, 'g')
#     # axs[1].plot(signal_c3a, 'r')
#     # axs[1].plot(psds_c3a_m, 'g')
#     # plt.show()
#
#     ringbuffer = manage_ringbuffer()
#     ringbuffer.append(hcon)
#     return hcon
#
#
# def print_normalized_vconses(labels, counter):
#     ringbuffer = manage_ringbuffer()
#     values = np.array(ringbuffer)
#     accuracy = 0
#     undefined = 0.5
#     for hcon in values:
#         mean = np.mean(values)
#         standard_deviation = np.std(values)
#         normalized_hcon = (hcon - mean) / standard_deviation if standard_deviation else hcon
#
#         if normalized_hcon > undefined:
#             calculated_label = 0
#         elif normalized_hcon < -undefined:
#             calculated_label = 1
#         else:
#             calculated_label = -1
#
#         if labels[counter] is not None and calculated_label == labels[counter]:
#             accuracy += 1
#
#         print(f'Clabel = {calculated_label} ({normalized_hcon})')
#         print(f'LabeL: {labels[counter]}')
#     accuracy /= len(labels)
#     print(f'Accuracy: {accuracy}')
