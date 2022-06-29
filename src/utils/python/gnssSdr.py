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
from mpl_toolkits.mplot3d import Axes3D
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

    def __init__(self, name, log_path, nTrack=None, ):
        ''' Constructor
        @param name [str]: name of this collection
        @param nTrack [int]: number of tracking channels to look at
        @param log_path [str]: the dir where the data is kept

        '''
        self.nTrack = nTrack
        self.log_path = log_path
        self.name = name
        self.tVec = np.arange(self.nTrack)
        
        self.samplingFreq = 3e6 # Hz

        self.dir_files = os.listdir(self.log_path)

        # init actions
        self.handle_acquire()
        self.handle_tracking()
        # self.handle_obs()

    ## ----- LOADERS ------
    def handle_obs(self,):
        # see fields in https://gnss-sdr.org/docs/sp-blocks/observables/#binary-output
        filename = self.log_path + '/observables.mat'
        obsDict = load_dumpMat(filename)
        self.obsArray = obsDict

    def handle_tracking(self,):
        trackArray = []
        for file in self.dir_files:
            if(file.startswith('nav_') and file.endswith('.mat')):
                filename = os.path.join(self.log_path, file)
                trackDict = load_dumpMat(filename)
                trackArray.append(trackDict)
        self.trackArray = trackArray
        if self.nTrack == None:
            # save away the found tracks
            self.nTrack = len(self.trackArray)
        else:
            self.nTrack = 1
        
    def handle_telem(self,):
        telemArray = []
        
        for file in self.dir_files:
            if(file.startswith('nav_')):
                filename = os.path.join(self.log_path, file)
                telemDict = load_dumpMat(filename)
                telemArray.append(telemDict)
                
        self.telemArray = telemArray

    def handle_acquire(self,):
        acqArray = []
        
        for file in self.dir_files:
            if(file.startswith('acq')):
                acqDict = load_dumpMat(os.path.join(self.log_path, file))
                # only load in positive acquired .mat dumps
                if acqDict['d_positive_acq'][0]==1:
                    acqArray.append(acqDict)
                # could alternatively load in only those with PRN == P
            
            # naming convention set in https://github.com/gnss-sdr/gnss-sdr/blob/main/src/algorithms/acquisition/gnuradio_blocks/pcps_acquisition.cc#L394
            # naming as "acq_dump_G_1C_ch_N_K_sat_P"   
            #   N is channel dump num from config
            #   K is dump number (increments)
            #   P is target PRN
            
        self.acqArray = acqArray
        self.nAcquire = len(self.acqArray)

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
        # result of test statistic
        test_stat = acqDict['test_statistic'][0]
        # 2d array results for acquisition 
        acq_grid = acqDict['acq_grid']
        f = np.arange(-dopplerMax, dopplerMax, dopplerStep)
        tau = np.linspace(0, 1023, np.size(acq_grid,1))
        F, T = np.meshgrid(f, tau)
        A = np.reshape(acq_grid, F.shape)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(F,T, A)
        ax.set_xlabel('Frequencies (Hz)')
        ax.set_ylabel('Delay (chips)')
        fig.colorbar(surf)
        
        self.printer("PRN %d Acquire Test Statistic: %.2f" % (prn, test_stat))
        

    def parseTelem(self, telemDict):
        ''' parse out the elements of the nav_data .mat 
        TBD what returns, 
        '''
        
        _time_sample = np.uint64(telemDict['tracking_sample_counter'][0])
        prn = np.uin32(telemDict['PRN'][0])

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

        # carreir error (filterred, raw) at output of PLL (Hz) 
        carrier_pll_filt_err = trackDict['carr_error_filt_hz'].T[0,sample_idx:]
        carrier_pll_err = trackDict['carr_error_hz'].T[0,sample_idx:]
        pll = carrier_pll_filt_err
        pll_raw = carrier_pll_err
        # code error (filtered, raw) at output of DLL (chips)
        code_error_filt_chips = trackDict['code_error_chips'].T[0,sample_idx:]
        dll = code_error_filt_chips
        code_error_chips = trackDict['code_error_filt_chips'].T[0,sample_idx:]
        dll_raw = code_error_chips
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

        return _time_s, carrier_dop, data_I, data_Q, dll, dll_raw, pll, pll_raw

    ## --- LOW LEVEL PLOTTING -----
    def trackPlots(self, ch):
        ''' run the tracking plots on a given channel  '''
        trackDict = self.trackArray[ch]
        _time_s, carrier_dop, dataI, dataQ, dll, dll_raw, pll, pll_raw = self.parseTrack(trackDict)
        fig, ax = plt.subplots()
        ax.plot(_time_s, carrier_dop, label='Doppler kHz')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Doppler Freq [kHz]')
        ax.set_title('Doppler Shift on Track 0')
        
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
        
        ax[2].plot(_time_s, pll_raw)
        ax[2].set_xlabel('Time (s)')
        ax[2].set_ylabel('Amplitude')
        ax[2].set_title('Raw PLL Discrim')
        
        ax[3].plot(_time_s, pll)
        ax[3].set_xlabel('Time (s)')
        ax[3].set_ylabel('Amplitude')
        ax[3].set_title('Filtered PLL Discrim')
        
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
        if self.nAcquire>0:
            # plot the first acquired signal
            self.acqPlots(0)
        else:
            self.printer("No Positive Acquires")
            
    def plot_observables(self, ):
        pass
    

    def plot_tracking(self):
        # see field names in https://gnss-sdr.org/docs/sp-blocks/tracking/#plotting-results-with-matlaboctave
        
        if self.nTrack == 1:
            self.trackPlots(0)
        else:
            for tIdx, trackDict in enumerate(self.trackArray):
                self.trackPlots(tIdx)

    ## ----------- UTILITIES ------------- ##
    def printer(self, strg):
        print("GNSS_SDR:: %s" %strg)
        
    

# if __name__ == "__main__":
    
#     print("gnssSdr.py startup\n")

#     ## -- PARSER ----
#     parser = argparse.ArgumentParser(description=''' 
#     This script is a class for doing gnss-sdr work ''')
    
#     # setup params
#     parser.add_argument('-dt','--timestep', action='store', nargs=1, type=int,
#                         default=312, help='the number of seconds between data')

l_path = '/home/groundpaq/darren_space/gnss-sdr/data'

# init
dar_gnss = GNSS_SDR(name='dar', nTrack=1, log_path=l_path+'/darren')
sp_gnss = GNSS_SDR(name='spain', nTrack=1, log_path=l_path+'/spain')

# actions
# %%
sp_gnss.plot_acq()
sp_gnss.plot_tracking()

# %% 
dar_gnss.plot_acq()
dar_gnss.plot_tracking()

# %%
plt.show()
print("gnssSdr.py end\n")

