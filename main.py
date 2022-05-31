import src.load_eeg as ld
import mne
from mne.utils import logger
import src.preprocessing_eeg as ppeeg
import src.performance_individual as ip
import os
import pandas as pd
import numpy as np

path_eeg = f'/content/drive/MyDrive/Colab Notebooks/PPGCC/EEG/data_brainvision/'
#path_eeg = f'datasets/data_brainvision/'

subjects = [f[:-5] for f in os.listdir(path_eeg) if f.endswith('.vhdr')]

path_events_dic = f'/content/preprocessing_EEG_with_MNE/datasets/event_stimulus_new_dict.json'
#path_events_dic = f'datasets/event_stimulus_new_dict.json'

path_targets = f'/content/preprocessing_EEG_with_MNE/datasets/list_subjects_groups.csv'
#path_targets = 'datasets/list_subjects_groups.csv'

#raise SystemExit

for sub in subjects:
    num_subject = str(sub[-4:])
    format_log = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    mne.set_log_file('/content/drive/MyDrive/Colab Notebooks/PPGCC/EEG/outputs_eeg/subject' + num_subject + '_log.log', output_format=format_log, overwrite=True)
    #mne.set_log_file('outputs_eeg/subject' + num_subject + '_log.log', output_format=format_log, overwrite=True)
    with mne.use_log_level(True):
        logger.info('# Pre-processing EEG data from subject ' + num_subject)

    eeg = ld.LoadEEG(path_eeg, sub)
    raw_data = eeg.read_eeg()
    events, events_dict = eeg.get_events(raw_data, path_events_dic)
    stimulus, stimulus_dict = eeg.select_stimulus(events, events_dict)
    
    if stimulus != None:
        pproc = ppeeg.PreprocessingEEG(raw_data, stimulus, stimulus_dict)
        pproc.run()

        df_targets = pd.read_csv(path_targets, dtype=str)
        list_control = df_targets['subject_control'].tolist()
        list_gifted = df_targets['subject_gifted'].tolist()

        if num_subject in list_control:
            group_subject = 'control'
        elif num_subject in list_gifted:
            group_subject = 'gifted'
        else:
            group_subject = 'undefined'

        iperformance = ip.PerformanceIndividual(events, stimulus, stimulus_dict)
        response_time_sub = iperformance.get_response_time()
        responses_expected, responses_obtained = iperformance.get_responses()
        accuracy = iperformance.get_accuracy()
        response_time_mean = np.mean(response_time_sub)
        with mne.use_log_level(True):
            logger.info('# Performance individual ')
            logger.info('Accuracy in the answers: ' + str(accuracy*100) + '%')
            logger.info('Mean response time: ' + str(response_time_mean) + 'ms')

        df_ip = pd.DataFrame()     
        df_ip['stimulus'] = iperformance.stimulus_name
        df_ip['responses_expected'] = responses_expected
        df_ip['responses_obtained'] = responses_obtained
        df_ip.insert(0, 'subject', num_subject)
        df_ip.insert(1, 'group', group_subject)

        df_ip.to_csv('/content/drive/MyDrive/Colab Notebooks/PPGCC/EEG/outputs_eeg/subject' + num_subject + '_ip.csv',  index = False)
        #df_ip.to_csv('outputs_eeg/subject' + num_subject + '_ip.csv', index = False)

        df_eeg, df_evoked = pproc.get_data_frame()
        df_eeg = df_eeg.rename(columns={"epoch":"trail"})
        df_eeg.insert(0, 'subject_name', num_subject)
        df_eeg.insert(1, 'group', group_subject)
        df_evoked.insert(0, 'subject', num_subject)
        df_evoked.insert(1, 'group', group_subject)

        df_eeg.to_csv('/content/drive/MyDrive/Colab Notebooks/PPGCC/EEG/outputs_eeg/subject' + num_subject + '_trials.csv',  index = False)
        df_evoked.to_csv('/content/drive/MyDrive/Colab Notebooks/PPGCC/EEG/outputs_eeg/subject' + num_subject + '_evoked.csv', index = False)
        #df_eeg.to_csv('outputs_eeg/subject' + num_subject + '_trials.csv', index = False)
        #df_evoked.to_csv('outputs_eeg/subject' + num_subject + '_evoked.csv', index = False)