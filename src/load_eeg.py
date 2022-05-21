import mne
import glob
import json
import os

class LoadEEG:
    def __init__(self, path: str, subject: str):
        self.path = path
        self.subject = subject

    def check_files(self):
        #Checking existence of all files
        n_files = len(glob.glob(self.path + self.subject + '*'))
        if n_files < 3:
            print('>>>>>>> There are missing files!')
            return None
        else:
            print('>>>>>>> All files are present!')
            name_files = [self.subject + '.eeg', self.subject + '.vhdr', self.subject + '.vmrk']
            files = [self.path + name for name in name_files]
            return files
    
    def read_eeg(self):
        #Reading EEG data
        files = self.check_files()
        raw_data = mne.io.read_raw_brainvision(files[1], preload=True) #Preloading raw data into memory
        return raw_data
    
    def get_events(self, raw_data: mne.io.Raw, dir_dict: str):
        #Get events point and its descriptors
        events, events_dict = mne.events_from_annotations(raw_data)
        #Load updated descriptors from json file
        with open(dir_dict, 'r') as f:
            events_dict = json.load(f)
        return events, events_dict
    
    def select_stimulus(self, events, events_dict):
        #Selecting only stimuli and response
        events_clean = []
        for i in range(len(events)):
            if i+1 < len(events):
                #If the event is not a subject response
                if (events[i][2] != 251) and (events[i][2] != 252):
                    if (events[i+1][2] == 251) or (events[i+1][2] == 252):
                        events_clean.append(events[i])
                        events_clean.append(events[i+1])

        #Selecting only stimuli without responses
        stimulus = [x for i, x in enumerate(events_clean) if i % 2 == 0]

        if len(stimulus) < 120:
            print('The subject performed less than 120 trials')
            return None, None
        else:
            print('The subject performed 75% of the total trails')

        #Descriptors that used
        stimulus_dict = {}
        for key, value in events_dict.items():
            if value in [x[2] for x in stimulus]:
                stimulus_dict.update({key: value})
        
        return stimulus, stimulus_dict