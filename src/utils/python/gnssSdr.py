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
        self.obsDict = load_dumpMat(filename)
        

    def handle_tracking(self,):
        trackArray = []
        for file in self.dir_files:
            if(file.startswith('tracking_') and file.endswith('.mat')):
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
        navArray = []
        
        for file in self.dir_files:
            if(file.startswith('nav_') and file.endswith('.mat')):
                filename = os.path.join(self.log_path, file)
                navDict = load_dumpMat(filename)
                navArray.append(navDict)
                
        self.navArray = navArray

    def handle_acquire(self,):
        acqArray = []
        
        for file in self.dir_files:
            if(file.startswith('acq') and file.endswith('.mat')):
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
        

    def parseNav(self, navDict):
        ''' parse out the elements of a specified nav_data .mat: a 1d with len = number of epochs
            (tracking integration times)
        
        '''
        _time_sample = np.uint64(navDict['tracking_sample_counter'][0])
        prn = np.uin32(navDict['PRN'][0])
        TOW_cur_sym_ms = np.double(navDict['TOW_at_current_symbol_ms'][0])
        TOW_preamble_ms = np.double(navDict['TOW_at_Preamble_ms'][0])
        nav_data = [np.int32(x) for x in navDict['nav_symbol'][0]]
        self.printer("done parseNav")

    def parsePrnTrack(self, prn, do_plot=True):
        '''parse out the tracking data for a specific PRN '''
        
        if self.trackArray is None:
            self.printer("No tracks to search")
        else:
            for trackDict in self.trackArray:
                this_prn = trackDict['PRN'][0][0]
                if this_prn==prn:
                    self.parseTrack(trackDict,do_plot)
                    break
                else:
                    continue
                
    def parseTrack(self, trackDict, do_plot=True):
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

        if do_plot:
            fig, ax = plt.subplots()
            ax.plot(_time_s, carrier_dop, label='Doppler kHz')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Doppler Freq [kHz]')
            ax.set_title('Doppler Shift on Track 0')
            
            fig2, ax = plt.subplots(3,2)
            ax = ax.flat
            ax[0].plot(data_I, data_Q, '.')
            ax[0].set_xlabel('I Data')
            ax[0].set_ylabel('Q Data')
            ax[0].set_title("Discrete-Time Constellation Diagram")
            
            ax[1].plot(_time_s, data_I,)
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

        return _time_s, carrier_dop, data_I, data_Q, dll, dll_raw, pll, pll_raw

    def parseObserve(self,):
        # rows = num Chan, columns = num of epochs
        carrier_doppler_hz = self.obsDict['Carrier_Doppler_hz']
        carrier_phase_cyc = self.obsDict['Carrier_phase_cycles']
        valid_pseudorange = self.obsDict['Flag_valid_pseudorange']
        prn_vec = self.obsDict['PRN']  # vec of headers for sat id 
        psuedorange_m = self.obsDict['Pseudorange_m']
        TOW_curr_sym_s = self.obsDict['TOW_at_current_symbol_s']
        print("done parse Observe")
        
        
    # HIGH LEVEL ACTIONS
    def plot_acq(self,):
        # see https://gnss-sdr.org/docs/sp-blocks/acquisition/#plotting-results-with-matlaboctave
        if self.nAcquire>0:
            # plot the first acquired signal
            self.parseAcq(self.acqArray[0])
        else:
            self.printer("No Positive Acquires")
            
    def plot_observables(self, ):
        self.parseObserve()
    
    def plot_nav(self,):
        for nIdx, navDict in enumerate(self.navArray):
            self.parseNav(navDict)

    def plot_tracking(self, prn=None, do_plot=True):
        ''' plot the tracking data
        @param prn [int]: (optional) choose a PRN satellite number, default None
        @param do_plot [bool]: enable track plotting 
        '''
        # see field names in https://gnss-sdr.org/docs/sp-blocks/tracking/#plotting-results-with-matlaboctave
        if prn:
            self.parsePrnTrack(prn)
            return
        if self.nTrack == 1:
            self.parseTrack(self.trackArray[0],do_plot=do_plot)
        else:
            for tIdx, trackDict in enumerate(self.trackArray):
                self.parseTrack(trackDict,do_plot=do_plot)

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
dar_gnss = GNSS_SDR(name='dar', nTrack=1, log_path=l_path+'/darren_0629_c')
sp_gnss = GNSS_SDR(name='spain', nTrack=1, log_path=l_path+'/spain')

# actions
# %%
sp_gnss.plot_acq()
sp_gnss.plot_tracking(prn=1)
# sp_gnss.plot_observables()

# %% 
dar_gnss.plot_acq()
dar_gnss.plot_tracking(prn=1)

# %%
plt.show()
print("gnssSdr.py end\n")

