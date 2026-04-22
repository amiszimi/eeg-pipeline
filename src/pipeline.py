"""
**EEG Signal Processing Pipeline**

A collection of functions for preprocessing and analyzing EEG data.
Built using MNE-Python.

Author: Aleksandra Szymanska
Project: EEG Signal Processing Portfolio Project
"""

import mne
import numpy as np
import matplotlib.pyplot as plt
from mne.preprocessing import ICA


def load_raw_eeg(filepath, preload=True):
    """
    Load raw EEG data from a .fif file.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the .fif file
    preload : bool
        Whether to load data into memory (default: True)
    
    Returns
    -------
    raw : mne.io.Raw
        Raw EEG data object
    """
    raw = mne.io.read_raw_fif(filepath, preload=preload)
    print(f"Loaded {len(raw.ch_names)} channels, {raw.times[-1]:.1f} seconds")
    return raw


def pick_eeg_channels(raw):
    """
    Select only EEG channels from raw data.
    
    Parameters
    ----------
    raw : mne.io.Raw
        Raw data object
    
    Returns
    -------
    raw : mne.io.Raw
        Raw data with only EEG channels
    """
    raw.pick('eeg')
    print(f"Selected {len(raw.ch_names)} EEG channels")
    return raw


def apply_bandpass_filter(raw, l_freq=0.1, h_freq=40.0):
    """
    Apply a bandpass filter to raw EEG data.
    
    Parameters
    ----------
    raw : mne.io.Raw
        Raw data object
    l_freq : float
        Low frequency cutoff (default: 0.1 Hz)
    h_freq : float
        High frequency cutoff (default: 40.0 Hz)
    
    Returns
    -------
    raw : mne.io.Raw
        Filtered raw data
    """
    raw.filter(l_freq=l_freq, h_freq=h_freq)
    print(f"Applied bandpass filter: {l_freq} - {h_freq} Hz")
    return raw


def remove_artifacts_ica(raw, n_components=15, random_state=42):
    """
    Remove eye blink artifacts using ICA.
    
    Parameters
    ----------
    raw : mne.io.Raw
        Raw data object (should be filtered first)
    n_components : int
        Number of ICA components (default: 15)
    random_state : int
        Random seed for reproducibility
    
    Returns
    -------
    raw : mne.io.Raw
        Cleaned raw data
    ica : mne.preprocessing.ICA
        Fitted ICA object (for inspection)
    """
    ica = ICA(n_components=n_components, random_state=random_state)
    ica.fit(raw)
    
    eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name=raw.ch_names[0])
    ica.exclude = eog_indices
    
    raw = ica.apply(raw)
    
    print(f"Removed {len(eog_indices)} artifact component(s): {eog_indices}")
    return raw, ica


def create_epochs(raw, events, event_id, tmin=-0.2, tmax=0.5):
    """
    Create epochs from raw data around events.
    
    Parameters
    ----------
    raw : mne.io.Raw
        Raw data object
    events : array
        Events array (n_events x 3)
    event_id : dict
        Dictionary mapping event names to IDs
    tmin : float
        Start time before event (default: -0.2 s)
    tmax : float
        End time after event (default: 0.5 s)
    
    Returns
    -------
    epochs : mne.Epochs
        Epochs object
    """
    epochs = mne.Epochs(
        raw,
        events,
        event_id=event_id,
        tmin=tmin,
        tmax=tmax,
        baseline=(None, 0),
        preload=True
    )
    print(f"Created {len(epochs)} epochs")
    return epochs


def compute_erp(epochs, condition=None):
    """
    Compute ERP (averaged evoked response) from epochs.
    
    Parameters
    ----------
    epochs : mne.Epochs
        Epochs object
    condition : str, optional
        Condition name to average (if None, average all)
    
    Returns
    -------
    evoked : mne.Evoked
        Averaged evoked response
    """
    if condition:
        evoked = epochs[condition].average()
    else:
        evoked = epochs.average()
    print(f"Computed ERP from {evoked.nave} trials")
    return evoked


def compute_band_power(raw, bands=None):
    """
    Compute power in standard frequency bands.
    
    Parameters
    ----------
    raw : mne.io.Raw
        Raw data object
    bands : dict, optional
        Dictionary of band names to (fmin, fmax) tuples
    
    Returns
    -------
    band_power : dict
        Dictionary of band names to power values
    relative_power : dict
        Dictionary of band n
