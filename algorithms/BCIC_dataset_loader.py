import math
from typing import List
import numpy as np

CHANNELS = [
            'Fz', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'C5',
            'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'CP3',
            'CP1', 'CPz', 'CP2', 'CP4', 'P1', 'Pz', 'P2',
            'POz']
TRIALS_SLICES = 1
SAMPLERATE = 250
TMIN = -2
TMAX = 5.5
RESAMPLE = False
datasets_folder = '/opt/datasets'
path = f'{datasets_folder}/BCICompetition_IV-2a/'
# Types of motor imagery
mi_types = {769: 'left', 770: 'right', 771: 'foot', 772: 'tongue', 783: 'unknown'}


def to_idxs_of_list_str(elements: List[str], list: List[str]):
    """
    Returns list of elements' indexes in string List
    """
    list_upper = [e.upper() for e in list]
    return [list_upper.index(el.upper()) for el in elements]


def calc_n_samples(tmin: float, tmax: float, samplerate: float):
    n_samples = int(round((tmax - tmin) * samplerate))
    return n_samples

def get_subject_fname(subject: int, training: int = 1):
    orgfiles_path = path + "Numpy_files/"  # Location of original subject-specific data files
    if training == 1:
        return orgfiles_path + 'A0' + str(subject) + 'T.npz'
    elif training == 0:
        return orgfiles_path + 'A0' + str(subject) + 'E.npz'
    else:
        print('Error: Illegal parameter')
    return None


def get_trials(subject: int, n_class: int = 4, ch_names: List[str] = CHANNELS, training: int = 1):
    ch_idxs = to_idxs_of_list_str(ch_names, CHANNELS)
    n_trials_max = 6 * 12 * n_class  # 6 runs with 12 trials per class
    n_samples = calc_n_samples(TMIN, TMAX, SAMPLERATE)
    fname = get_subject_fname(subject, training)

    print('  - Load data of subject %d from file: %s' % (subject, fname))
    data = np.load(fname)

    raw = data['s'].T
    events_type = data['etyp'].T
    events_position = data['epos'].T
    events_duration = data['edur'].T
    artifacts = data['artifacts'].T

    # raw = MIDataLoader.BP_notch_filtering(raw)  # Optional bandpass and notch filtering (NOT IMPORTANT!!!)

    startrial_code = 768
    starttrial_events = events_type == startrial_code
    idxs = [i for i, x in enumerate(starttrial_events[0]) if x]

    # Originally we have 288 trial, but some have artifacts
    # trial_ind is the index of the original 288 trial dataset
    # pl_trial_ind is the index where a valid data set is stored
    # in pl_data array
    trial_ind = 0
    pl_trial_ind = 0
    subject_data, subject_labels = np.full((n_trials_max, len(ch_idxs), n_samples), -1), \
                                   np.full((n_trials_max), -1)
    # For any trial specified by its idxs valus
    for index in idxs:
        try:
            if artifacts[0, trial_ind] == 0:
                type_e = events_type[0, index + 1]
                class_e = mi_types[type_e]

                if (n_class == 2 and (type_e >= 769 and type_e <= 770)) or \
                        (n_class == 3 and (type_e >= 769 and type_e <= 771)) or \
                        (n_class == 4 and (type_e >= 769 and type_e <= 772)):

                    # Store the trial specific label with following class encoding:
                    # MI action   | BCIC_IV2a code | class label
                    # ------------------------------------------
                    # Left hand          769              1 -> 0
                    # Right hand         770              2 -> 1
                    # Both feet          771              3 -> 2
                    # Tongue             772              4 -> 3
                    # Unknown            783             -1 (invalid trial)

                    # Assume we have class vector like this one here:
                    # class_vec = [class1, class2, class3, class4]
                    # Then pl_labels is the index to the class to which current
                    # trials belongs.
                    subject_labels[pl_trial_ind] = type_e - 768 - 1

                    start = events_position[0, index]
                    stop = start + events_duration[0, index]
                    # Copy trial data into pl_data array
                    for i, channel in enumerate(ch_idxs):
                        trial = raw[channel, start:stop]
                        if len(trial) != 1875:
                            print('get_trials(): Illegal length')

                        # Copy part of channel data into pl_data
                        start_idx = int(TMIN * SAMPLERATE)
                        for idx in range(n_samples):
                            subject_data[pl_trial_ind, i, idx] = float(trial[start_idx + idx])

                    pl_trial_ind = pl_trial_ind + 1

            else:
                x_temp = 0  # noop
            #                    print("  - Trial %d is marked as an artifact and ignored" % (trial_ind))

            trial_ind = trial_ind + 1
        except Exception as e:
            print("get_trials(): Exception occured", e)
            continue
    return subject_data, subject_labels


def load_subject(subject: int, n_class: int, ch_names: List[str] = CHANNELS):
    subject_data, subject_labels = get_trials(subject, n_class, ch_names)

    return subject_data, subject_labels


def load_subjects_data(subjects: List[int], n_class: int, ch_names: List[str] = CHANNELS, tmin=-2, tmax=5.5,
                       equal_trials: bool = True, ignored_runs: List[int] = []):
    TMIN, TMAX = tmin, tmax
    subjects.sort()
    trials_max = 6 * 12 * n_class * TRIALS_SLICES
    subject_trials_max = trials_max
    samples = math.floor(((tmax - tmin) * SAMPLERATE) / TRIALS_SLICES)
    preloaded_data = np.zeros((len(subjects), subject_trials_max, len(ch_names), samples))
    preloaded_labels = np.full((len(subjects), subject_trials_max), -1)
    for s_idx, subject in enumerate(subjects):
        preloaded_data[s_idx], preloaded_labels[s_idx] = load_subject(subject, n_class, ch_names)
    return preloaded_data, preloaded_labels
