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


class PlotUsrp():
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
        elif typ=="c":
            self.dtype = np.complex64
    ## ----- LOADERS ------
    def handle_usrp(self,):
        # see fields in https://gnss-sdr.org/docs/sp-blocks/observables/#binary-output
        self.complex = np.fromfile(open(self.log_path),dtype=self.dtype)
        if self.dtype==np.complex64:
            self.I = np.real(self.complex)
            self.Q = np.imag(self.complex)
        elif self.dtype==np.float32 or np.int16:
            self.I = self.complex[0::2]
            self.Q = self.complex[1::2]
        self.nSample = len(self.Q)
        self.dt = 1/self.samplingFreq
        if self.nSample*self.dt != float(self.nSec):
            print("num_samples*dt != duration")
            exit()
        
        self.time_s = np.arange(self.nSample)/self.samplingFreq

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
        if self.dtype==np.complex64:
            freqs = np.fft.fftshift(np.fft.fftfreq(self.nSample, d=self.dt))
        else:
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
if __name__ == "__main__":
    
    print(f"{__file__} startup\n")

    ## -- PARSER ----
    parser = argparse.ArgumentParser(description=''' 
    This script is a class for quickview of usrp recorded data ''')
    
    # setup params
    parser.add_argument('-n','--name', action='store', type=str,
                        default='usrp_samples.dat', help='the filename to analyze')
    parser.add_argument('-fs','--sampFreq', action='store', type=int,
                        default=3e6, help='the sampling freq of the collection (MHz)')
    parser.add_argument('-nSec','--duration', action='store', type=float,
                        default=5, help='the duration of the collection (s)')
    parser.add_argument('-t','--type', action='store', type=str,
                        default='f', choices=['i', 'f', 'c'], 
                        help='the datatype.  interleaved are \'i\' and \'f\'; complex as \'c\'')
    
    # get arguments
    args = parser.parse_args(sys.argv[1:])
    
    if args.name is None:
        print(f"{__file__} requires a save name for file output")
        exit
    else:
        if not args.name.endswith('.dat'):
            print(f"{__file__} requires the save name with extension .dat")
            exit
    
    trial = PlotUsrp(l_path=args.name, nSec=args.duration, Fs=args.sampFreq*1e6, typ=args.type)


    # actions
    trial.plot_usrp()


    plt.show()
    print(f"{__file__} end\n")


