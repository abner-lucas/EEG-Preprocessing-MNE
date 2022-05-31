import mne
import autoreject as ar

from mne.utils import logger

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
        with mne.use_log_level(True):
            logger.info('# Setting the reference channel for eyes movement')
            self.set_channel_types()

            logger.info('# Setting the 10-20 pattern in the channel position')
            self.set_montage()

            logger.info('# Band-pass filter (high-pass = 0.1Hz and low-pass = 35Hz)')
            self.filter_h_l()

            logger.info('# Segmenting ERP signal: 200 ms before stimulus and 4000 ms after')
            self.erp_epochs()

            #logger.info('# Compute global rejection thresholds')
            #self.bias_rejection()

            logger.info('# Selecting and rebuilding bad electrodes with interpolation (PREP pipeline)')
            self.fit_bad_interpolation()

            logger.info('# Filter high-pass (1Hz)')
            self.filter_h()

            logger.info('# Apply ICA')
            self.fit_ICA()

            logger.info('# Segmenting ERP signal: Baseline correction by subtracting the mean potential amplitude from the 200 ms interval immediately preceding the stimulus at each epoch')
            self.baseline_correction()

            logger.info('# Apply CAR')
            self.set_CAR()

            self.select_channels()
    
    def set_channel_types(self):
        self.raw_data.set_channel_types({'EOG1': 'eog', 'EOG2': 'eog', 'EOGz': 'eog'})
        with mne.use_log_level(True):
            logger.info('Channel types:           %s' % self.raw_data.get_channel_types())
    
    def set_montage(self):
        self.raw_data.set_montage('standard_1020')
        with mne.use_log_level(True):
            logger.info('Channel positions 10-20: %s' % self.raw_data.ch_names)

    def filter_h_l(self):
        self.f_data = self.raw_data.copy().filter(l_freq=0.1, h_freq=35)
    
    def filter_h(self):
        self.f_epochs_clean = self.epochs_clean.copy().filter(l_freq=1, h_freq=None)
        with mne.use_log_level(True):
            logger.info('Frequency range: %sHz, %sHz' % (self.f_epochs_clean.info['highpass'], self.f_epochs_clean.info['lowpass']))
    
    def erp_epochs(self):
        tinitial = -0.2
        tfinal = 4.0

        picks = mne.pick_types(self.f_data.info, eeg=True, eog=True, stim=True, meg=False, ecg=False, exclude='bads')
        self.epochs = mne.Epochs(self.f_data.copy(), self.stimulus, self.stimulus_dict, picks=picks,
                            tmin=tinitial, tmax=tfinal, baseline=None, preload=True)
        #                    tmin=tinitial, tmax=tfinal, baseline=(None, 0), preload=True)
        with mne.use_log_level(True):
            logger.info('Number of trials: %s' % self.epochs.events.shape[0])
    
    def bias_rejection(self):
        self.bias_reject = ar.get_rejection_threshold(self.epochs) # noqa
        with mne.use_log_level(True):
            logger.info('Bias rejection threshold: EEG - %s , EOG - %s' % (self.bias_reject['eeg'], self.bias_reject['eog']))

    def fit_bad_interpolation(self):
        ransac = ar.Ransac(verbose=True)
        self.epochs_clean = ransac.fit_transform(self.epochs)
        self.epochs_clean.info['bads'] = ransac.bad_chs_
        with mne.use_log_level(True):
            logger.info('Bad channels: %s' % ransac.bad_chs_)

    def fit_ICA(self):
        random_state = 42       # ensures ICA is reproducable each time it's run
        ica_n_components = .99  # Specify n_components as a decimal to set % explained variance
        method = 'fastica'      # Use FastICA for ICA decomposition
        tfinal = 4.0

        #Compute ICA
        ica = mne.preprocessing.ICA(n_components=ica_n_components, random_state=random_state, method=method)
        #ica.fit(self.f_epochs_clean, reject=self.bias_reject, tstep=tfinal)
        ica.fit(self.f_epochs_clean, tstep=tfinal, verbose=True)

        #Detect EOG related components using correlation
        eog_idx, eog_scores = ica.find_bads_eog(self.f_epochs_clean, ch_name=['EOG1', 'EOG2', 'EOGz'])
        
        #Exclude EOG-related components
        ica.exclude = eog_idx

        #Apply ICA to the data
        self.f_epochs_clean_ica = ica.apply(self.f_epochs_clean.copy(), exclude=ica.exclude)
        with mne.use_log_level(True):
            logger.info('Number of components: %s' % ica.n_components_)
            logger.info('ICA components that are related to EOG artifacts: %s' % eog_idx)
        
    def baseline_correction(self):
        self.f_epochs_clean_ica.apply_baseline(baseline=(None, 0))

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