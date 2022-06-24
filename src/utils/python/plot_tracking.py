from random import sample
import h5py
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys, os, shutil


def load_trackDump(fname: str) -> dict:
    ''' 
    @param: fname [str]: the name of the file to parse through (ends in .mat)
    @return [dict]: dict of the data in the dumped file
    '''    
    

    arrays = {}
    f = h5py.File(fname)
    for k, v in f.items():
        arrays[k] = np.array(v)

    return arrays

def plot_tracking():
    samplingFreq = 3e6  # Hz
    channels = 1
    chVec = np.arange(channels)
    ax = np.zeros_like(chVec)
    track_log_path = '/home/groundpaq/darren_space/gnss-sdr/data'

    
    trackArray = []
    for ch in chVec:
        filename = track_log_path + '/tracking_ch_%d.mat' % ch
        trackDict = load_trackDump(filename)
        trackArray.append(trackDict)

    
    if channels == 1:
        sample_idx = 0
        code_freq_chips = trackDict['code_freq_chips']
        if sample_idx > 0 and sample_idx<len(code_freq_chips):
            sample_idx = len(code_freq_chips) - sample_idx
        else:
            sample_idx = 1

        fig, ax = plt.subplots()
        prn_start_time_s = trackDict['PRN_start_sample_count'].T[0,sample_idx:]/samplingFreq
        carrier_dop = trackDict['carrier_doppler_hz'].T[0,sample_idx:]/1000

        ax.plot(prn_start_time_s, carrier_dop, label='Doppler kHz')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Doppler Freq [kHz]')
        ax.set_title('Doppler Shift on Ch 0')
    else:
        # plot doppler
        for chIdx, ch in enumerate(chVec):
            sample_idx = 0
            code_freq_chips = trackArray[chIdx]['code_freq_chips']
            if sample_idx > 0 and sample_idx<len(code_freq_chips):
                sample_idx = len(code_freq_chips) - sample_idx
            else:
                sample_idx = 1

            fig, ax[chIdx] = plt.subplots()
            prn_start_time_s = trackArray[chIdx]['PRN_start_sample_count'].T[0,sample_idx:]/samplingFreq
            carrier_dop = trackArray[chIdx]['carrier_doppler_hz'].T[0,sample_idx:]/1000

            ax[chIdx].plot(prn_start_time_s, carrier_dop, label='Doppler kHz')
            ax[chIdx].set_xlabel('Time (s)')
            ax[chIdx].set_ylabel('Doppler Freq [kHz]')
            ax[chIdx].set_title('Doppler Shift on Ch %d' % chIdx)

if __name__ == "__main__":
    
    print("plot_tracking.py startup\n")

    ## -- PARSER ----
    parser = argparse.ArgumentParser(description=''' 
    This script is a class for doing gnss-sdr work ''')
    
    # setup params
    parser.add_argument('-dt','--timestep', action='store', nargs=1, type=int,
                        default=312, help='the number of seconds between data')

    plot_tracking()

    plt.show()
    print("plot_tracking.py end\n")