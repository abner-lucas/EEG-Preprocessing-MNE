import mne
import matplotlib.pyplot as plt

path = f'data_brainvision/'
name_file = 'Metzler0004'
file = path + name_file + '.vhdr'

raw_data = mne.io.read_raw_brainvision(file, preload=True)

events_stimulus, event_stimulus_dict = mne.events_from_annotations(raw_data)

mne.viz.plot_events(events_stimulus, event_id=event_stimulus_dict, sfreq=raw_data.info['sfreq'])
plt.show()