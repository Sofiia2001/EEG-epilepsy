import mne
import os


def create_raw_object(file_path):
    # Creating the raw edf object using mne library
    return mne.io.read_raw_edf(file_path)


def visualize_data(raw_object, duration_sec, start_time, eeg_color):
    # Plotting the EEG data
    raw_object.plot(duration=duration_sec, start=start_time, color=dict(mag='black', grad='b', eeg=eeg_color, eog='k', ecg='m',
     emg='k', ref_meg='steelblue', misc='k', stim='k',
     resp='k', chpi='k'), bad_color="maroon")


def find_all_paths(path):
    # Goes into all possible directories starting from initial "path"
    # goes into all sub-directories to find .edf files
    list_of_files = {}
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(".edf"):
                list_of_files[filename] = os.sep.join([dirpath, filename])
    return list_of_files