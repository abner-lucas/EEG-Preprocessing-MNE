import mne
import matplotlib.pyplot as plt

path = f'data_brainvision/'
name_file = 'Metzler0004'
file = path + name_file + '.vhdr'

raw_data = mne.io.read_raw_brainvision(file, preload=True)

raw_data.plot(duration=1)
plt.show()