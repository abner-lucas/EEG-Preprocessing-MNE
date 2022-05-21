import mne
import autoreject as ar

class PreprocessingEEG:
    def __init__(self, raw_data: mne.io.Raw, stimulus: list, stimulus_dict: dict):
        self.raw_data = raw_data
        self.stimulus = stimulus
        self.stimulus_dict = stimulus_dict
        self.f_data = None
        self.epochs = None
        self.bias_reject = None
        self.epochs_clean = None
        self.f_epochs_clean = None
        self.f_epochs_clean_ica = None
        self.f_epochs_clean_ica_car = None
        self.p_f_data = None
        
        #Execution of the methods
    def run(self):
        self.set_channel_types()
        self.set_mnotage()
        self.filter_h_l()
        self.erp_epochs()
        self.bias_rejection()
        self.fit_bad_interpolation()
        self.filter_h()
        self.fit_ICA()
        self.set_CAR()
        self.select_channels()
    
    def set_channel_types(self):
        #Setting the reference channel for eyes movement.
        self.raw_data.set_channel_types({'EOG1': 'eog', 'EOG2': 'eog', 'EOGz': 'eog'})
        print('Channel types: %s' % self.raw_data.ch_types)
    
    def set_mnotage(self):
        #Setting the 10-20 pattern in the channel position
        self.raw_data.set_montage('standard_1020')
        print('Channel positions 10-20: %s' % self.raw_data.ch_names)

    def filter_h_l(self):
        #Band-pass filter (high-pass = 0.1Hz and low-pass = 35Hz)
        self.f_data = self.raw_data.copy().filter(l_freq=0.1, h_freq=35)
    
    def filter_h(self):
        #Filter high-pass
        self.f_epochs_clean = self.epochs_clean.copy().filter(l_freq=1, h_freq=None)
        print('Frequency range: %s, %s' % (self.f_epochs_clean.info['lowpass'], self.f_epochs_clean.info['highpass']))
    
    def erp_epochs(self):
        #Segmenting ERP signal:
        # - 200 ms before stimulus and 4000 ms after
        # - Baseline correction by subtracting the mean potential amplitude from the 200 ms interval immediately preceding the stimulus at each epoch
        tinitial = -0.2
        tfinal = 4.0

        picks = mne.pick_types(self.f_data.info, eeg=True, eog=True, stim=True, meg=False, ecg=False, exclude='bads')
        self.epochs = mne.Epochs(self.f_data.copy(), self.stimulus, self.stimulus_dict, picks=picks,
                            tmin=tinitial, tmax=tfinal, baseline=(None, 0), event_repeated='drop',
                            preload=True)
        print('Number of epochs: %s' % self.epochs.events.shape[0])
    
    def bias_rejection(self):
        self.bias_reject = ar.get_rejection_threshold(self.epochs) # noqa
        print('Bias rejection threshold: %s' % self.bias_reject)

    def fit_bad_interpolation(self):
        #Selecting and rebuilding bad electrodes with interpolation (PREP pipeline)
        ransac = ar.Ransac(verbose=True)
        self.epochs_clean = ransac.fit_transform(self.epochs)
        self.epochs_clean.info['bads'] = ransac.bad_chs_
        print('Bad channels: %s' % ransac.bad_chs_)

    def fit_ICA(self):
        random_state = 42       # ensures ICA is reproducable each time it's run
        ica_n_components = .99  # Specify n_components as a decimal to set % explained variance
        tfinal = 4.0

        #Compute ICA
        ica = mne.preprocessing.ICA(n_components=ica_n_components, random_state=random_state)
        ica.fit(self.f_epochs_clean, reject=self.bias_reject, tstep=tfinal)

        #Detect EOG related components using correlation
        eog_idx, eog_scores = ica.find_bads_eog(self.f_epochs_clean, ch_name=['EOG1', 'EOG2', 'EOGz'])
        
        #Exclude EOG-related components
        ica.exclude = eog_idx

        #Apply ICA to the data
        self.f_epochs_clean_ica = ica.apply(self.f_epochs_clean.copy(), exclude=ica.exclude)
        print('ICA components that are related to EOG artifacts: %s' % eog_idx)

    def set_CAR(self):
        #Apply CAR (common average reference)
        self.f_epochs_clean_ica_car = self.f_epochs_clean_ica.copy().set_eeg_reference('average', ch_type='eeg', projection=True)
        self.f_epochs_clean_ica_car.apply_proj()

    def select_channels(self):
        #Selecting only the frontal, parietal, and reference lobe channels for eye movement
        self.p_f_data = self.f_epochs_clean_ica_car.copy().pick_channels(['F1','F2','F3','F4','F5','F6','F7','F8','Fz','P1','P2','P3','P4','P5','P6','P7','P8','Pz'])
        
    #Methods to get the data
    def get_data_frame(self):
        df_eeg = self.p_f_data.to_data_frame()
        evoked = self.p_f_data.average()
        df_evoked = evoked.to_data_frame()
        return df_eeg, df_evoked