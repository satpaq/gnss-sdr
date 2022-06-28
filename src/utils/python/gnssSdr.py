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



def load_dumpMat(fname: str) -> dict:
    ''' 
    @param: fname [str]: the name of the file to parse through (ends in .mat)
    @return [dict]: dict of the data in the dumped file
    '''    
    arrays = {}
    f = h5py.File(fname)
    for k, v in f.items():
        arrays[k] = np.array(v)

    return arrays



class GNSS_SDR():
    ''' class for gathering data from running GNSS-SDR '''

    def __init__(self, nChan, log_path):
        ''' Constructor
        
        @param nChan [int]: number of channels to look at
        @param log_path [str]: the dir where the data is kept

        '''
        self.nChan = nChan
        self.log_path = log_path

        self.chVec = np.arange(self.nChan)
        
        self.samplingFreq = 3e6 # Hz


        # init actions
        self.handle_acquire()
        self.handle_tracking()
        self.handle_obs()

    ## ----- LOADERS ------
    def handle_obs(self,):
        # see fields in https://gnss-sdr.org/docs/sp-blocks/observables/#binary-output
        obsArray = []
        for ch in self.chVec:
            filename = self.log_path + '/observ_ch_.mat'
            obsDict = load_dumpMat(filename)
            obsArray.append(obsDict)
        self.obsArray = obsArray

    def handle_tracking(self,):
        trackArray = []
        for ch in self.chVec:
            filename = self.log_path + '/tracking_ch_%d.mat' % ch
            trackDict = load_dumpMat(filename)
            trackArray.append(trackDict)
        self.trackArray = trackArray

    def handle_acquire(self,):
        acqArray = []
        for ch in self.chVec:
            filename = self.log_path + '/acq_1c_dump_G_1C_ch_%d_1_sat_1.mat' % ch
            acqDict = load_dumpMat(filename)
            acqArray.append(acqDict)
        self.acqArray = acqArray

    ### ---- DICT PARSERS -------
    def parseAcq(self, acqDict):
        ''' parse out the elements of the acquisition .mat 
        TBD what returns, for now return _time_s, acq_doppler
        '''
        
        _time_sample = acqDict['sample_counter'][0]
        prn = acqDict['PRN'][0]
        in_power = acqDict['input_power'][0]  # ??

        # overall params
        nDwell = acqDict['num_dwells'][0]
        dopplerStep = acqDict['doppler_step'][0]
        dopplerMax = acqDict['doppler_max'][0]
        thresh = acqDict['threshold'][0]
        isDetected = acqDict['d_positive_acq'][0]
        # course estimate of doppler shift (Hz)
        acq_doppler = acqDict['acq_doppler_hz'][0]
        # course estimate of time delay (samp)
        acq_delay = acqDict['acq_delay_samples'][0]

        # 2d array results for acquisition 
        acq_grid = acqDict['acq_grid']
        f = np.arange(-dopplerMax, dopplerMax, dopplerStep)
        tau = np.linspace(0, 1023, np.size(acq_grid,1))
        
        fig, ax = plt.subplots()
        surf = ax.plot_surface(f, tau, acq_grid)
        fig.colorbar(surf)


    def parseTrack(self, trackDict, ):
        ''' parse out the contents of the track .mat 
        TBD what fields you want returned, for now just _time_s, carrier_dop
        '''
        sample_idx = 0
        code_freq_chips = trackDict['code_freq_chips']
        if sample_idx > 0 and sample_idx<len(code_freq_chips):
            sample_idx = len(code_freq_chips) - sample_idx
        else:
            sample_idx = 0

        
        # time since track start (s)
        _time_s = trackDict['PRN_start_sample_count'].T[0,sample_idx:]/self.samplingFreq
        # prn under test
        prn = trackDict['PRN'].T[0,sample_idx:]
        # status of lock test
        carrier_lock = trackDict['carrier_lock_test'].T[0,sample_idx:]
        # doppler shift (Hz)
        carrier_dop = trackDict['carrier_doppler_hz'].T[0,sample_idx:]/1000

        # NOT PRESENT
        # # carreir error (filterred, raw) at output of PLL (Hz) 
        # carrier_pll_filt_err = trackDict['carrier_error_filt_hz'].T[0,sample_idx:]
        # carrier_pll_err = trackDict['carr_error_hz'].T[0,sample_idx:]
        
        # code error (filtered, raw) at output of DLL (chips)
        code_error_filt_chips = trackDict['code_error_chips'].T[0,sample_idx:]
        code_error_chips = trackDict['code_error_filt_chips'].T[0,sample_idx:]
        # code frequency (chip/s)
        code_freq_chips = trackDict['code_freq_chips'].T[0,sample_idx:]
        # code frequency rate (chips/s/s)
        code_freq_rate_chips = trackDict['code_freq_rate_chips'].T[0,sample_idx:]
        # accumulated carrier phase (rad)
        acc_carrier_phase = trackDict['acc_carrier_phase_rad'].T[0,sample_idx:]
        # carrier to noise ratio (dB-Hz)
        cn0_dB = trackDict['CN0_SNV_dB_Hz'].T[0,sample_idx:]

        # I and Q of correlator
        data_I = trackDict['Prompt_I'].T[0,sample_idx:]
        data_Q = trackDict['Prompt_Q'].T[0,sample_idx:]

        return _time_s, carrier_dop, data_I, data_Q, code_error_filt_chips, code_error_chips

    ## --- LOW LEVEL PLOTTING -----
    def trackPlots(self, ch):
        ''' run the tracking plots on a given channel  '''
        trackDict = self.trackArray[ch]
        _time_s, carrier_dop, dataI, dataQ, dll, dll_raw = self.parseTrack(trackDict)
        fig, ax = plt.subplots()
        ax.plot(_time_s, carrier_dop, label='Doppler kHz')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Doppler Freq [kHz]')
        ax.set_title('Doppler Shift on Ch 0')
        
        fig2, ax = plt.subplots(3,2)
        ax = ax.flat
        ax[0].plot(dataI, dataQ, '.')
        ax[0].set_xlabel('I Data')
        ax[0].set_ylabel('Q Data')
        ax[0].set_title("Discrete-Time Constellation Diagram")
        
        ax[1].plot(_time_s, dataI,)
        ax[1].set_xlabel('Time (s)')
        ax[0].set_ylabel('I Data')
        ax[1].set_title("Bits of Nav Message")
        
        # empty 2, 3,
        
        ax[4].plot(_time_s, dll_raw)
        ax[4].set_xlabel('Time (s)')
        ax[4].set_ylabel('Amplitude')
        ax[4].set_title('Raw DLL Discrim')
        
        ax[5].plot(_time_s, dll)
        ax[5].set_xlabel('Time (s)')
        ax[5].set_ylabel('Amplitude')
        ax[5].set_title('Filtered DLL Discrim')
        
        
    
    def acqPlots(self, ch):
        ''' run the acquisition plots on a given channel '''
        acqDict = self.acqArray[ch]
        self.parseAcq(acqDict)


    # HIGH LEVEL ACTIONS
    def plot_acq(self,):
        # see https://gnss-sdr.org/docs/sp-blocks/acquisition/#plotting-results-with-matlaboctave
        if self.nChan == 1:
            self.acqPlots(0)
        else:
            for chIdx, ch in enumerate(self.chVec):
                self.acqPlots(chIdx)
            
    def plot_observables(self, ):
        pass
    

    def plot_tracking(self):
        # see field names in https://gnss-sdr.org/docs/sp-blocks/tracking/#plotting-results-with-matlaboctave
        
        if self.nChan == 1:
            self.trackPlots(0)
        else:
            for chIdx, ch in enumerate(self.chVec):
                self.trackPlots(chIdx)

    
#%%
if __name__ == "__main__":
    
    print("plot_tracking.py startup\n")

    ## -- PARSER ----
    parser = argparse.ArgumentParser(description=''' 
    This script is a class for doing gnss-sdr work ''')
    
    # setup params
    parser.add_argument('-dt','--timestep', action='store', nargs=1, type=int,
                        default=312, help='the number of seconds between data')

    l_path = '/home/groundpaq/darren_space/gnss-sdr/data'

    # init
    a_gnss = GNSS_SDR(nChan=1, log_path=l_path)


    # actions
    # %%
    a_gnss.plot_tracking()
    # a_gnss.plot_acq()

    plt.show()
    print("plot_tracking.py end\n")
# %%
