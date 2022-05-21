import os
import src.load_eeg as ld
import src.preprocessing_eeg as ppeeg

#path = f'/content/drive/MyDrive/Colab Notebooks/PPGCC/EEG/data_brainvision/'
path_eeg = f'datasets/data_brainvision/'
subjects = [f[:-5] for f in os.listdir(path_eeg) if f.endswith('.vhdr')]
path_events_dic = f'datasets/event_stimulus_new_dict.json'

#raise SystemExit

for sub in subjects:
    eeg = ld.LoadEEG(path_eeg, sub)
    raw_data = eeg.read_eeg()
    events, events_dict = eeg.get_events(raw_data, path_events_dic)
    stimulus, stimulus_dict = eeg.select_stimulus(events, events_dict)
    print(stimulus_dict)
    if stimulus != None:
        pproc = ppeeg.PreprocessingEEG(raw_data, stimulus, stimulus_dict)
        pproc.run()
        df_eeg = pproc.get_data_frame()
        df_eeg = df_eeg.rename(columns={"epoch":"trail"})

        #df_eeg.to_csv('/content/preprocessing_EEG_with_MNE/datasets/' + subject + '_epochs_clean.csv')
        df_eeg.to_csv('outputs_eeg/' + sub + '.csv')
    
    print('\n')
    print(f'{sub} done!')
    print('++++++++++++++++++++++++++++++++++++++++++++++++\n')