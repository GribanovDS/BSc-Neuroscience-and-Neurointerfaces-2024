# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 10:13:14 2025

@author: marin
"""

import numpy as np
import mne
import matplotlib.pyplot as plt
import os

#%% Specify folder
folder = 'data_example'
os.listdir(folder)

#%%

data = np.load(f'eeg.npy') # first column is unix-time
ch_names = ['O1', 'T3', 'T4', 'O2']
sfreq = 250
info = mne.create_info(ch_names, sfreq)
raw_filt = mne.io.RawArray(data[:, 1:].T, info)
raw_filt.plot(title='EEG filt')


#%% Filtered EEG

data = np.load(f'{folder}/eeg.npy') # first column is unix-time
ch_names = ['T3-O1', 'T4-O2']
sfreq = 250
info = mne.create_info(ch_names, sfreq)
raw_filt = mne.io.RawArray(data[:, 1:].T, info)
raw_filt.plot(title='EEG filt')

#%% Raw EEG

data = np.load(f'{folder}/raw_eeg.npy') # first column is unix-time
ch_names = ['T3-O1', 'T4-O2']
sfreq = 250
info = mne.create_info(ch_names, sfreq)
raw = mne.io.RawArray(data[:, 1:].T, info)
raw.plot(title='EEG raw')

#%% Resistances

resistances = np.load(f'{folder}/resistances.npy')

for ch in ['T3', 'T4', 'O1', 'O2']:
    data = resistances[resistances[:, 1] == ch]
    data = data[:, [0, 2]].astype(float)
    data[:, 1] /=1e3 # from Ohms to Kiloohms
    plt.plot(data[:, 0], data[:, 1], label=ch)
    
plt.ylabel('KOhms', rotation='horizontal', ha='right')
plt.xlabel('unix-time')
plt.legend()
plt.tight_layout()
plt.show()

#%% infinity resistances
ch = 'O1'
resistances[resistances[:, 1] == ch]

#%% Spectra

psd = np.load(f'{folder}/psd.npy') 
freqs = np.linspace(0, 125, 1251, endpoint=True)

plt.plot(freqs, psd[100, 1])
plt.xlabel('frequency, Hz')
plt.ylabel('power', rotation='horizontal', ha='right')
plt.xlim(0, 125)
plt.grid()

#%% MEMS

acc = np.load(f'{folder}/acc.npy') 
gyroscope = np.load(f'{folder}/gyroscope.npy') 

figure, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))

axes[0].plot(acc[:, 0], acc[:, 1:], label=['X', 'Y', 'Z'])
axes[1].plot(gyroscope[:, 0], gyroscope[:, 1:], label=['X', 'Y', 'Z'])

axes[0].set_title('accelerometer')
axes[1].set_title('gyroscope')

axes[0].set_ylabel('g', rotation='horizontal', ha='right')
axes[1].set_ylabel('rad/sec', rotation='horizontal', ha='right')

axes[0].legend()
axes[1].legend()

axes[1].set_xlabel('unix-time')

#%% Photoplethysmogram

data = np.load(f'{folder}/ppg.npy') 
ch_names = ['ppg']
sfreq = 100
info = mne.create_info(ch_names, sfreq)
raw_ppg = mne.io.RawArray(data[:, 1:].T, info)
raw_ppg.plot(title='PPG')

#%% Cardio metrics

# - `timestampMilli` (int): timestamp in milliseconds
# - `heartRate` (float): heart rate (beats/min)
# - `stressIndex` (float): stress level score
# - `kaplanIndex` (float): heart rate variability index
# - `hasArtifacts` (bool): presence of artifacts
# - `skinContact` (bool): presence of skin contact
# - `motionArtifacts` (bool): presence of motion artifacts
# - `metricsAvailable` (bool): flag of metrics availability

cardio = np.load(f'{folder}/cardio.npy') 
plt.plot(cardio[:, 0], cardio[:, 1], label='heart rate')
plt.xlabel('unix-time')
plt.show()

#%% Emotions

# - `timestampMilli` (int): timestamp in milliseconds
# - `focus` (float): level of focus
# - `chill` (float): level of relaxation
# - `stress` (float): stress level
# - `anger` (float): anger level
# - `selfControl` (float): level of self-control

emotions = np.load(f'{folder}/emotions.npy') 
plt.plot(emotions[:, 0], emotions[:, 1:], label=['focus', 'chill', 'stress', 'anger', 'selfControl'])
plt.xlabel('unix-time')
plt.legend()
plt.ylabel('percent', rotation='horizontal', ha='right')
plt.tight_layout()
plt.show()

#%% Productivity metrics

# - `timestampMilli` (int): timestamp
# - `fatigueScore` (float): fatigue level
# - `reverseFatigueScore` (float): inverse fatigue level. Anti-fatigue.
# - `gravityScore` (float): cognitive load
# - `relaxationScore` (float): degree of relaxation
# - `concentrationScore` (float): concentration
# - `productivityScore` (float): productivity score (not normalized).
# - `currentValue` (float): normalized productivitySocre score and in the range from 0 to 1.
# - `alpha` (float): normalized alpha power in the range from 0 to 1.
# - `productivityBaseline` (float): baseline productivityScore
# - `accumulatedFatigue` (float): accumulated fatigue
# - `fatigueGrowthRate` (float): growth rate of accumulated fatigue

prod_metrics_states = np.load(f'{folder}/prod_metrics_states.npy')
plt.plot(prod_metrics_states[:, 0], prod_metrics_states[:, 8], label='alpha')
plt.xlabel('unix-time')
plt.legend()
plt.show()


#%% Physiological states 

# - `timestampMilli` (int): timestamp
# - `relaxation` (float): level of relaxation (probability)
# - `fatigue` (float): level of fatigue (probability)
# - `none` (float): uncertain state (probability)
# - `concentration` (float): level of concentration (probability)
# - `involvement` (float): level of involvement (probability)
# - `stress` (float): level of stress (probability)
# - `nfbArtifacts` (bool): presence of NFB artifacts
# - `cardioArtifacts` (bool): presence of artifacts in the NFB signal

phy_states = np.load(f'{folder}/phy_states.npy')
plt.plot(phy_states[:, 0], phy_states[:, 1:-2], label=['relaxation', 'fatigue', 'none', 'concentration', 'involvement', 'stress'])
plt.xlabel('unix-time')
plt.legend()
plt.ylabel('probability', rotation='horizontal', ha='right')
plt.tight_layout()
plt.show()
