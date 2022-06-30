''' file to load in dump mat's from gnss-sdr trials 
for output plotting on remote, we use jupyter notebook style cell blocks.  

created: Darren Reis
date: 6/26/22
Higher Ground
'''

#%% 
from random import sample
import h5py
import numpy as np
import matplotlib.pyplot as plt
#matplotlib inline
import argparse
import sys, os, shutil


class USRP_RAW():
    ''' class for gathering data from running USRP 'rx_samples_to_file' -SDR '''

    def __init__(self, l_path, nSec=5, Fs=3e6, typ='f'):
        ''' Constructor
        
        @param l_path [str]: the dir where the data is kept

        '''
        self.log_path = l_path
        self.samplingFreq = Fs # Hz
        self.nSec = nSec # s
        self.setType(typ)
        
        
        # init actions
        self.handle_usrp()

    def setType(self,typ):
        if typ=='f':
            self.dtype = np.float32
        elif typ=='s':
            self.dtype = np.int16
        else:
            self.dtype = np.int16
    ## ----- LOADERS ------
    def handle_usrp(self,):
        # see fields in https://gnss-sdr.org/docs/sp-blocks/observables/#binary-output
        self.complex = np.fromfile(open(self.log_path),dtype=self.dtype)
        self.I = self.complex[0::2]
        self.Q = self.complex[1::2]
        self.nSample = len(self.Q)
        self.dt = 1/self.samplingFreq
        if self.nSample*self.dt != float(self.nSec):
            print("num_samples*dt != duration")
            exit()
        
        self.time_s = np.arange(self.nSample)/self.samplingFreq
        # print("done parseing")

    ## --- LOW LEVEL PLOTTING -----
    def plot_time(self):
        ''' run the tracking plots on a given channel  '''
        fig, ax = plt.subplots()
        ax.plot(self.time_s, self.I, label='Real')
        ax.plot(self.time_s, self.Q, label='Imag')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Signal')
        ax.set_title('Time Domain Signal')
        
    def plot_fft(self,):
        fig2, ax = plt.subplots()
        sig_fft = np.fft.fftshift(np.fft.fft(self.complex))
        sig_dB = 20*np.log10(np.abs(sig_fft))
        freqs = np.fft.fftshift(np.fft.fftfreq(2*self.nSample, d=self.dt))
        
        ax.plot(freqs,sig_dB)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Power (dB)")
        ax.set_title("Power Spectrum")
        
    
    # HIGH LEVEL ACTIONS
    def plot_usrp(self,):        
        self.plot_time()
        self.plot_fft()
        
    
    
#%%
# if __name__ == "__main__":
    
#     print("plot_usrp.py startup\n")

#     ## -- PARSER ----
#     parser = argparse.ArgumentParser(description=''' 
#     This script is a class for quickview of usrp recorded data ''')
    
#     # setup params
#     parser.add_argument('-n','--name', action='store', nargs=1, type=str,
#                         default='usrp_samples.dat', help='the filename to analyze')
#     parser.add_argument('-fs','--sampFreq', action='store', nargs=1, type=int,
#                         default=3e6, help='the sampling freq of the collection')
#     parser.add_argument('-nSec','--duration', action='store', nargs=1, type=float,
#                         default=5, help='the duration of the collection (s)')
    
gnss_path = '/home/groundpaq/darren_space/gnss-sdr/data/'
usrp_path = '/home/groundpaq/darren_space/gnss-sdr/work/'


# TODO: make name load dynamic


# init
# a_trial = USRP_RAW(l_path=usrp_path, nSec=5, Fs=3e6, typ='i')   # default with no signal
    # with gps signal turn on
#    a_trial = USRP_RAW(l_path='/var/log/gpaq/usrp_float_2s.dat', nSec=2, Fs=3e6, typ='f')
#    a_trial = USRP_RAW(l_path='/var/log/gpaq/usrp_short_2s.dat', nSec=2, Fs=3e6, typ='i')

# real GPS signals
# a_trial = USRP_RAW(l_path=usrp_path + 'usrp_L1_60s_2m.dat', nSec=60, Fs=2e6, typ='i')
# a_trial = USRP_RAW(l_path=usrp_path + 'usrp_L1_60s.dat', nSec=60, Fs=3e6, typ='i')
# a_trial = USRP_RAW(l_path=usrp_path + 'usrp_L1_30s.dat', nSec=30, Fs=3e6, typ='f')

# 6/29
# off_trial = USRP_RAW(l_path=usrp_path + 'usrp_mini_short_5s.dat', nSec=5, Fs=3e6, typ='i')
# bias_trial = USRP_RAW(l_path=usrp_path + 'usrp_mini_short_bias_5s.dat', nSec=5, Fs=3e6, typ='i')
# sig_gen = USRP_RAW(l_path= usrp_path + 'usrp_mini_sigen_4s_4m.dat', nSec=4, Fs=4e6, typ='i')
    # rf collected at 1575.52 instead of 1575.42M
gain_trial = USRP_RAW(l_path=usrp_path + 'usrp_mini_20s_4m_e.dat', nSec=20, Fs=4e6, typ='i')


# actions
# off_trial.plot_usrp()
# bias_trial.plot_usrp()
# sig_gen.plot_usrp()
gain_trial.plot_fft()


plt.show()
print("plot_usrp.py end\n")


# %%
