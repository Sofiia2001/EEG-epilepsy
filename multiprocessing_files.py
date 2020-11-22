import mne
import time
from oct2py import Oct2Py
import os
from tqdm import tqdm
import multiprocessing as mp

octave = None

def init_octave():
    global octave
    octave = Oct2Py()

    octave.addpath('../../eeglab_current/eeglab2020_0/plugins/clean_rawdata1.00')
    octave.addpath('../../eeglab_current/eeglab2020_0/plugins/Biosig3.3.0/biosig/eeglab')
    octave.addpath('../../eeglab_current/eeglab2020_0/plugins/Biosig3.3.0/biosig/t200_FileAccess')
    octave.addpath('../../eeglab_current/eeglab2020_0/plugins/Biosig3.3.0/biosig/t250_ArtifactPreProcessingQualityControl/')
    octave.addpath('../../eeglab_current/eeglab2020_0/functions/popfunc')
    octave.addpath('../../eeglab_current/eeglab2020_0/functions/guifunc')
    octave.addpath('../../eeglab_current/eeglab2020_0/functions/adminfunc')
    octave.addpath('../../eeglab_current/eeglab2020_0/functions/sigprocfunc')
    octave.addpath('../../eeglab_current/eeglab2020_0/functions/miscfunc')

    octave.addpath('../../matlab_R2020b_glnxa64/sys/java/jre/glnxa64/jre/bin')


def single_edf_preprocessing(file_path):
    # Reading from the .edf file
    # print(f"\nTrying to open {file_path}")
    initial_file_name = file_path.split("/")[-1]
    print('---'*100)
    print(f'OPENING {initial_file_name}\n\n'.upper())
    try:
        print(f"Reading data from the {initial_file_name}...")
        EEG_raw = octave.pop_readedf(file_path)
        print(f"File was successfully {initial_file_name} read!")
    except Exception as ex:
        print("The input file cannot be accessed.")
        print(ex)
        return ex
    # Cleaning of raw data
    try:
        print("Cleaning the data...")
        EEG_cleaned = octave.clean_rawdata(EEG_raw, [], [0.5, 1], [], [], "off", "off", [])
    except Exception as ex:
        print("There is an error while cleaning the raw data.")
        return ex
    # We turn off the functionality which is dedicated to removing specific parts of one file
    # This is performed for the reason that we do not intend to delete data fragments to keep the timeline
    # the same as in the raw version

    # Saving the cleaned data into .edf file
    file_name = "filtered_" + initial_file_name
    new_file_path = '/'.join(file_path.split("/")[:-1]) + f"/{file_name}"
    try:
        # octave.pop_writeeeg(EEG_cleaned, file_name, "TYPE", "EDF")
        octave.pop_writeeeg(EEG_cleaned, new_file_path, "TYPE", "EDF")
        print(f"Writing the cleaned data into {file_name}...")
    except Exception as ex:
        print("There are some troubles with saving the .edf file.")
        return ex
    os.remove(file_path)
    print(f'\n\nSAVING {file_name}'.upper())
    print('---'*100)
    print('\n\n')
    return new_file_path
    # return file_name


def create_raw_object(file_path):
    # Creating the raw edf object using mne library
    return mne.io.read_raw_edf(file_path)


def visualize_data(raw_object, duration_sec, start_time, eeg_color):
    # Plotting the EEG data
    raw_object.plot(duration=duration_sec, start=start_time, color=dict(mag='black', grad='b', eeg=eeg_color, eog='k',
                                                                        ecg='m',
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


# TRYING TO PERFORM MULTIPROCESSING ON FIVE EDF FILES
def main():
    # start_time = time.time()
    files = list(find_all_paths('edf').values())
    with mp.Pool(10, initializer=init_octave) as pool:
        pool.map(single_edf_preprocessing, files)

    # duration = time.time() - start_time
    # print(f"Total time: {duration}")


if __name__ == '__main__':
    # files = list(find_all_paths('edf').values())
    # print(len(files))
    main()
    # print('---'*100)