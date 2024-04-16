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
import argparse
import sys, os, shutil
import glob



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
       
class MonitorTools():
    ''' class for gathering data from running GNSS-SDR '''

    def __init__(self, name,  log_path, nTrack=8, debug_level=0,):
        ''' Constructor
        @param name [str]: name of this collection
        @param nTrack [int]: number of tracking channels to look at
        @param log_path [str]: the dir where the data is kept

        '''
        self.nTrack = nTrack
        self.log_path = log_path
        self.name = name
        self.debugLvl = debug_level
        self.samplingFreq = 4e6 # Hz

        self.dir_files = os.listdir(self.log_path)       
        

    ## ----- LOADERS ------
    
    # arrays of files 
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
        
    def handle_nav(self,):
        navArray = []
        
        for file in self.dir_files:
            if(file.startswith('nav_') and file.endswith('.mat')):
                filename = os.path.join(self.log_path, file)
                navDict = load_dumpMat(filename)
                navArray.append(navDict)
                
        self.navArray = navArray
    
    # single dump file
    def handle_pvt(self,):
        filename = os.path.join(self.log_path, 'PVT.mat')
        pvtDict = load_dumpMat(filename)
        self.pvtDict = pvtDict

    def handle_obs(self,):
        # see fields in https://gnss-sdr.org/docs/sp-blocks/observables/#binary-output
        filename = self.log_path + '/observables.mat'
        self.obsDict = load_dumpMat(filename)
        
    
    ### ---- DICT PARSERS -------
    def parseAcq(self, acqDict, do_plot=False):
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
        
        if do_plot:
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
        

    def parseNav(self, navDict, do_plot=False):
        ''' parse out the elements of a specified nav_data .mat:
            a 1d with len = number of epochs
            (tracking integration times)
        
        '''
        
        ''' this doesn't totally make sense; why are these 1d vectors and not a list of 1d vecs???
        i'm labeling what i see but i'm skeptical i understand things.  @TODO: '''
        
        # int of the sample count at the start of each epoch.  these are diff=40000 or nearly
        epoch_sample = navDict['tracking_sample_counter'].T[0]  # (nEpoch,1)
        prn = navDict['PRN'].T[0]  # (nEpoch, 1)
        # somehow these two vectors are almost =; doesn't make sense
        TOW_cur_sym_ms = navDict['TOW_at_current_symbol_ms'].T[0]  # (nEpoch,1)
        TOW_preamble_ms = navDict['TOW_at_Preamble_ms'].T[0]  # (nEpoch,1)
        # this is the output of a specific epoch.  again, this would make more sense as a list of vecs
        nav_data = navDict['nav_symbol'].T[0]  # (nEpoch, 1)
        
        if do_plot:
            fig, ax = plt.subplots()

        self.printer("done parseNav for PRN %d" % prn[0])
        

    def parsePrnTrack(self, prn, do_plot=True):
        '''parse out the tracking data for a specific PRN '''
        
        if self.trackArray is None:
            self.printer("No tracks to search")
        else:
            for trackDict in self.trackArray:
                # handle case of A) only 1 tracked PRN  B) multiple tracked PRNs
                dictDim =  np.ndim(trackDict['PRN'])
                if dictDim == 1:
                    this_prn = trackDict['PRN'][0]
                elif dictDim == 2:
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
        prn = trackDict['PRN'].T[0,sample_idx:][0]
        
        # status of lock test
        carrier_lock = trackDict['carrier_lock_test'].T[0,sample_idx:]
        # doppler shift (Hz)
        carrier_dop = trackDict['carrier_doppler_hz'].T[0,sample_idx:]/1000

        # carrier error (filterred, raw) at output of PLL (Hz) 
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
        # code_freq_rate_chips = trackDict['code_freq_rate_chips'].T[0,sample_idx:]
        # accumulated carrier phase (rad)
        acc_carrier_phase = trackDict['acc_carrier_phase_rad'].T[0,sample_idx:]
        # accumulated code phase (samples)
        rem_code_phase_sample = trackDict['rem_code_phase_sample']
        # carrier to noise ratio (dB-Hz)
        cn0_dB = trackDict['CN0_SNV_dB_Hz'].T[0,sample_idx:]

        # I and Q of correlator
        data_I = trackDict['Prompt_I'].T[0,sample_idx:]
        data_Q = trackDict['Prompt_Q'].T[0,sample_idx:]

        if do_plot:
            print("Plot Tracking of PRN %d" % prn)
            
            # # carrier error output
            # fig, ax3 = plt.subplots()
            # ax3.plot(_time_s, carrier_dop, label='Doppler kHz')
            # ax3.set_xlabel('Time (s)')
            # ax3.set_ylabel('Doppler Freq [kHz]')
            # ax3.set_title('Doppler Shift on PRN %d' % prn)
            
            fig2, ax = plt.subplot_mosaic([['tl','tr'], ['ml','mr'], ['bl','br']], constrained_layout=True)
            
            ax['tl'].plot(data_I, data_Q, '.')
            ax['tl'].set_xlabel('I Data')
            ax['tl'].set_ylabel('Q Data')
            ax['tl'].set_title("Constellation Diagram")
            
            ax['tr'].plot(_time_s, carrier_lock,)
            # ax['tr'].set_xlabel('Time (s)')
            ax['tr'].set_ylabel('Carrier Lock')
            ax['tr'].set_title("PRN %d Carrier Lock" % prn)
                        
            ax['ml'].plot(_time_s, pll)
            ax['ml'].set_xlabel('Time (s)')
            ax['ml'].set_ylabel('Amplitude')
            ax['ml'].set_title('Filtered PLL Discrim')
        
            ax['mr'].plot(_time_s, dll)
            ax['mr'].set_xlabel('Time (s)')
            ax['mr'].set_ylabel('Amplitude')
            ax['mr'].set_title('Filtered DLL Discrim')

            ax['bl'].plot(_time_s, acc_carrier_phase)
            ax['bl'].set_title('Accum Carrier Phase')
            ax['bl'].set_ylabel('Phase (rad)')
            ax['bl'].set_xlabel('Time (s)')
            
            ax['br'].plot(_time_s, rem_code_phase_sample)
            ax['br'].set_title('Remaining Code Phase')
            ax['br'].set_ylabel('Phase (sample)')
            ax['br'].set_xlabel('Time (s)')
            
        return _time_s, carrier_dop, data_I, data_Q, dll, dll_raw, pll, pll_raw, rem_code_phase_sample, acc_carrier_phase, 

    def parseObserve(self,do_plot=False):
        # index 1 is number of the epoch
        # index 2 is the track channel idx
        
        ## MAT 2d results:  each is (nEpoch, nTrack)
        prn_mat = self.obsDict['PRN']  # vec prn's tracked 
        carrier_doppler_hz_mat = self.obsDict['Carrier_Doppler_hz']
        carrier_phase_cyc_mat = self.obsDict['Carrier_phase_cycles']
        valid_pseudorange_mat = self.obsDict['Flag_valid_pseudorange']
        psuedorange_m_mat = self.obsDict['Pseudorange_m']
        TOW_curr_sym_s_mat = self.obsDict['TOW_at_current_symbol_s']
        rx_time_s_mat = self.obsDict['RX_time']
       
        nEpoch, nTrack = np.shape(prn_mat)
        # index into MAT objs with 
        e_idx, t_idx = np.nonzero(prn_mat)
        nPoints = len(e_idx)  # number of obervable samples
        ## FLAT (nPoints) array of results
        
        rx_time_s = rx_time_s_mat[e_idx].T[0]  # rx time (s)
        tVec = rx_time_s - rx_time_s[0]  # time of sample from collection start (s)
        
        # these are all mat's of size (nPoints, nTrack);  
        #   the cell element mat[i,t] corresponds to time tVec[i], and sat prn_vec[i]
        prn_vec = prn_mat[e_idx].T 
        carrier_doppler_hz = carrier_doppler_hz_mat[e_idx].T  # carrier dopp in Hz
        carrier_phase_cyc = carrier_phase_cyc_mat[e_idx].T  
        # valid_pseudorange = valid_pseudorange_mat[e_idx,t_idx]  # unused
        psuedorange_m = psuedorange_m_mat[e_idx].T
        TOW_curr_sym_s = TOW_curr_sym_s_mat[e_idx]  # time of week of curr symbol
        
        
        # flattened versions  (maybe useful, but be careful because these are like multiple samples
        #   at a specific time)  
        carrier_doppler_hz_flat = carrier_doppler_hz_mat[e_idx,t_idx]
        carrier_phase_cyc_flat = carrier_phase_cyc_mat[e_idx,t_idx]
        # etc.
        
        # @TODO: the right way to do this would be to break into short structs
        #   dedicated to a PRN and record the time and estimates linked to that PRN, then have a 
        #   dict or something of tracks.  
       
        if do_plot:
            fig, ax = plt.subplots(2,1,sharex=True)
            # if it were useful, we could print text on the plot for every PRN to mark the 
            #   source of each of the line sections  
            
            ax[0].plot(tVec, carrier_phase_cyc.T)
            ax[0].set_ylabel('Carrier Phase [Cycles]')
            ax[0].set_title('Carrier Phase Accum on 8 Channels')
            
            ax[1].plot(tVec, carrier_doppler_hz.T)
            ax[1].set_xlabel('Time From Start (s)')
            ax[1].set_ylabel('Doppler Freq [kHz]')
            ax[1].set_title('Doppler Freq on 8 Channels')
        
        self.printer("done parse Observe")
        
    def parsePvt(self,do_plot=False):
        ## 1d results of position solution:  each is (nSolu)
        
        rx_time_s = self.pvtDict['RX_time'].T[0] # GPS time
        user_clk_offset_s = self.pvtDict['user_clk_offset'].T[0]  # time of user clk (in ref to GPS time)
        TOW_curr_sym_ms = self.pvtDict['TOW_at_current_symbol_ms'].T[0] 
        valid_sats = self.pvtDict['valid_sats'].T[0]  # num of valid sats for solu
        
        pos_type = self.pvtDict['solution_type'].T[0]  # 0:xyz-ecef, 1:enu-baseline
        pos_x = self.pvtDict['pos_x'].T[0]
        vel_x = self.pvtDict['vel_x'].T[0]
        # etc.
        
        self.printer("done parse PVT")
        
        
    # HIGH LEVEL ACTIONS
    def plot_acq(self,do_plot=False):
        self.handle_acquire()
        # see https://gnss-sdr.org/docs/sp-blocks/acquisition/#plotting-results-with-matlaboctave
        if self.nAcquire>0:
            # plot the first acquired signal
            self.parseAcq(self.acqArray[0],do_plot)
        else:
            self.printer("No Positive Acquires")

    def plot_tracking(self, prn=None, do_plot=True):
        ''' plot the tracking data
        @param prn [int]: (optional) choose a PRN satellite number, default None
        @param do_plot [bool]: enable track plotting 
        '''
        self.handle_tracking()
        # see field names in https://gnss-sdr.org/docs/sp-blocks/tracking/#plotting-results-with-matlaboctave
        if prn:
            self.parsePrnTrack(prn)
            return
        else:
            for tIdx, trackDict in enumerate(self.trackArray):
                self.parseTrack(trackDict,do_plot=do_plot)

    def plot_nav(self,do_plot=False):
        self.handle_nav()
        for nIdx, navDict in enumerate(self.navArray):
            self.parseNav(navDict,do_plot)   
            
    def plot_observables(self, do_plot=False):
        self.handle_obs()
        if do_plot:
            print("Plot Observables")
        self.parseObserve(do_plot)
    
    def plot_pvt(self,do_plot=False):
        self.handle_pvt()
        if do_plot:
            print("Plot PVT")
        self.parsePvt(do_plot)

    
    ## ----------- UTILITIES ------------- ##
    def printer(self, strg):
        if self.debugLvl > 1:
            print("GNSS_SDR:: %s" %strg)
        
    

if __name__ == "__main__":
    
    print(f"{__file__} startup\n")

    dr_path = os.path.abspath('.') + '/data'
    do_plot = True


    # select which gnss-sdr output dir to grab mat's to analyze
    fname_a = '/darren/mini_0706_30s_4m_short_g50_trialA'
    fname_b = '/darren/mini_0706_60s_4m_short_g50_trialB'
    fname_sbas_17_1 = '/sbas/geofix1_config17_30s_900mhz_take1'
    fname_sbas_17_2 = '/sbas/geofix1_config17_30s_900mhz_take2'
    fname_sbas_17_3 = '/sbas/geofix1_config17_30s_900mhz_take3'
    fname_sbas_18_1 = '/sbas/geofix1_config18_30s_900mhz_take1'
    fname_sbas_18_2 = '/sbas/geofix1_config18_30s_900mhz_take2'
    fname_sbas_bruce = '/sbas/mini_0718_4m_bruce_lna_t1'   # has a problem... re process
    fname_sbas_bruce2 = '/sbas/mini_0718_4m_bruce_lna_t2'
    fname = fname_sbas_bruce2
    dar = MonitorTools(name='dar', log_path=dr_path+fname)


    print("DARREN PLOTS")
    # dar.plot_acq()
    # dar.plot_tracking(prn=23)
    dar.plot_tracking()
    # dar.plot_observables(do_plot)
    # dar.plot_nav(do_plot)
    # dar.plot_pvt(do_plot)
    # %%
    plt.show()
    print(f"{__file__} end\n")

