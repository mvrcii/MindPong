import mne
import numpy
import numpy as np
from config import CONFIG
from data.datasets.datasets import DATASETS
from scipy import integrate
from numpy_ringbuffer import RingBuffer

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


def calculate_small_laplacian(signal1, signal2, signal3, signal4):
    counter = 0
    length = len(signal1)
    result = list()

    while counter < length:
        average = (signal1[counter] + signal2[counter] + signal3[counter] + signal4[counter]) / 4
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
    signal_average = calculate_small_laplacian(signal_list[2], signal_list[3], signal_list[4], signal_list[5])

    length = len(signal_list[0])
    counter = 0
    while counter < length:
        signal_c3a.append(signal_list[0][counter] - signal_average[counter])
        signal_c4a.append(signal_list[1][counter] - signal_average[counter])
        counter += 1

    return signal_c3a, signal_c4a


def perform_multitaper(signal, jobs=-1):
    psds, freqs = mne.time_frequency.psd_array_multitaper(x=np.array(signal), sfreq=CONFIG.EEG.SAMPLERATE,
                                                          bandwidth=32.0, n_jobs=jobs)
    psds_abs = np.abs(psds)
    return psds_abs, freqs


def perform_rfft(signal):
    fft_spectrum = np.fft.rfft(signal)
    freq = np.fft.rfftfreq(len(signal), d=1 / CONFIG.EEG.SAMPLERATE)
    fft_spectrum_abs = np.abs(fft_spectrum)

    return fft_spectrum_abs, freq


def integrate_psd_values(signal, frequencyList):
    # calculate alpha frequency array
    counter = 0
    length = len(frequencyList)
    alpha_band_power = list()
    requested_frequency_range = list()

    # TODO: evaluate if necessary !!!
    while counter < length:
        if 15.0 >= frequencyList[counter] >= 9.0:
            alpha_band_power.append(signal[counter])
            requested_frequency_range.append(frequencyList[counter])
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


def get_dataset_and_perform_algorithm():
    # TODO: initialize ringbuffer 1x
    r = RingBuffer(capacity=144, dtype=np.float)
    # Load BCIC dataset
    dataset = DATASETS['BCIC']
    used_subjects = [5]
    validation_subjects = []
    n_class = 2
    ch_names = ['C3', 'C4', 'FC1', 'FC2', 'CP1', 'CP2']
    # ch_names = dataset.CONSTANTS.CHANNELS
    ds_tmin = 0
    ds_tmax = 4

    CONFIG.set_eeg_config(dataset.CONSTANTS.CONFIG)  # Data set specific default initialization
    CONFIG.EEG.set_times(ds_tmin, ds_tmax, dataset.CONSTANTS.CONFIG.CUE_OFFSET)

    print("  - ds_tmin, ds_tmax =", ds_tmin, ds_tmax)
    preloaded_data, preloaded_labels = dataset.load_subjects_data(used_subjects + validation_subjects, n_class,
                                                                  ch_names)

    for i in range(144):
        # 1. Spatial Filtering
        signal_c3a, signal_c4a = calculate_spatial_filtering(preloaded_data[0][i][:][:])

        # 2. PSD calculation via FFT
        psds_c3a_f, freq_c3a_f = perform_rfft(signal_c3a)
        psds_c4a_f, freq_c4a_f = perform_rfft(signal_c4a)

        # 3. Alpha Band Power calculation
        area_c3 = integrate_psd_values(psds_c3a_f, freq_c3a_f)
        area_c4 = integrate_psd_values(psds_c4a_f, freq_c4a_f)
        # print(f'C3pow = {area_c3}, C4pow = {area_c4}')
        # print(f'Hcon: {area_c4-area_c3}')

        # Derive cursor control signals
        hcon = area_c4 - area_c3
        r.append(hcon)
        values = np.array(r)
        mean = np.mean(values)
        standard_deviation = np.std(values)
        normalized_hcon = (hcon - mean) / standard_deviation if standard_deviation else hcon

        # label stuff
        label = preloaded_labels[0][i]
        if label == 0:
            side = 'Left'
        elif label == 1:
            side = 'Right'
        else:
            side = 'Nicht definiert'

        print(f'Hcon: {normalized_hcon}')
        print(f'Label: {label} ({side})\n')


if __name__ == '__main__':
    get_dataset_and_perform_algorithm()
