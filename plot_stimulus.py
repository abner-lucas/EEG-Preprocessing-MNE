import mne
import matplotlib.pyplot as plt

path = f'data_brainvision/'
name_file = 'Metzler0004'
file = path + name_file + '.vhdr'

raw_data = mne.io.read_raw_brainvision(file, preload=True)

events_stimulus, event_stimulus_dict = mne.events_from_annotations(raw_data)

#save events_stimulus em txt
with open(f'datasets/events_stimulus_{name_file}.txt', 'w') as f:
    for item in events_stimulus:
        f.write("%s\n" % item)

#plot somente 30 events_stimulus
mne.viz.plot_events(events_stimulus, event_id=event_stimulus_dict, sfreq=raw_data.info['sfreq'])
plt.show()