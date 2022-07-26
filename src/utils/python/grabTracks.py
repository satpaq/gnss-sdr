''' grabTracks.py
@author: Darren Reis
@date: 7/26/22


example file for how to grab tracks from a 'multi' .conf output

run the processing by doing 

grab data and store it in as    work/FILE.dat
edit the /work/gnss-sdr_GPS_L1_sbas_multi.conf
    - change the .dump_dir to data/sbas/multi/NAME
    - do    mkdir -p data/sbas/multi/NAME 
    

gnss-sdr 
with args: 
"-c", "work/gnss-sdr_GPS_L1_sbas_multi.conf",
"--signal_source", "work/FILE.dat",
"--log_dir", "data/sbas/multi/NAME",

then run the class in this file in the manner below to grab out the gps and geo tracks

to see the output on remote, you need to have jupyter set up.  you also need the python
interpreter to be set as the pipenv based on this pipfile.  that way you have the right
modules for your jupyter.  
then you should be able to have the interactive terminal show up, and you can see actions
as you hover the mouse over, you'll see something like "run above".  
that launches the interactive window which is a jupyter thing, and should show plots
'''

import h5py
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys, os
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


class GnssTrack():
    ''' class for grabbing track outputs of a .conf processing '''
    def __init__(self, data_path, nTrack=8, debug_level=0, name=None):
        ''' Constructor
        @param name [str]: name of this collection
        @param nTrack [int]: number of tracking channels to look at
        @param log_path [str]: the dir where the data is kept

        '''
        self.nTrack = nTrack
        if data_path.endswith('.dat'):
            data_path = data_path.split('.')[0]
        self.data_path = data_path
        
        if name is None:
            name = os.path.basename(data_path)
        elif name.endswith(".dat"):
            name = name.split('.')[0]
        self.name = name
        
        self.debugLvl = debug_level
        self.samplingFreq = 4e6 # Hz

        self.handle_tracking()
        
    def handle_tracking(self,):
        geoArray = []
        gpsArray = []
        # only tracking files are loaded
        all_files = glob.glob(self.data_path + '/**/*.mat',recursive=True)
        nTrack = 0
        track_files = []
        for file in all_files:
            if 'tracking' in file:
                nTrack += 1
                track_files.append(file)  # if we want it
                base = os.path.basename(file)
                # filename = os.path.join(self.data_path, file)  # get abs fname
                trackDict = load_dumpMat(file)
                try:
                    hgTrack = self.make_hgTrack(trackDict)
                except:
                    self.printer("bad track exception, %s" % base, 1) 
                    # that track didn't succeed, move on dear friend
                    continue
                if base.startswith('1C'):
                    gpsArray.append(hgTrack)
                elif base.startswith('S1'):
                    geoArray.append(hgTrack)
                elif base.startswith('1B'):  
                    pass  # someday come back and include Galileo in the gpsArray() 
            
        # store away raw, if we want it
        self.nTrack = nTrack   
        self.track_files = track_files
        # store away hgTrack dicts
        self.gpsTracks = gpsArray  
        self.geoTracks = geoArray
        
     
    def make_hgTrack(self, trackDict):
        ''' take in the raw GNSS-SDR dict, output a hgTrack dict'''
        
        # valid track check
        if np.ndim(trackDict['PRN_start_sample_count']) == 1:
            raise NameError("Bad Track")
        
        sample_idx = 0
        code_freq_chips = trackDict['code_freq_chips']
        if sample_idx > 0 and sample_idx<len(code_freq_chips):
            sample_idx = len(code_freq_chips) - sample_idx
        else:
            sample_idx = 0

        # time since track start (s)
        time_s = trackDict['PRN_start_sample_count'].T[0,sample_idx:]/self.samplingFreq
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

        dicto = {
            'prn' : prn,
            'time_s' : time_s,
            'carrier_lock' : carrier_lock,
            'carrier_dop' : carrier_dop,
            'data_I' : data_I,
            'data_Q' : data_Q,
            'pll' : pll,
            'dll' : dll,
            'rem_code_phase_sample' : rem_code_phase_sample,
            'acc_carrier_phase' : acc_carrier_phase,
        }        
        return dicto
       
    # def parsePrnTrack(self, prn, do_plot=True):
    #     '''parse out the tracking data for a specific PRN '''
        
    #     if self.trackArray is None:
    #         self.printer("No tracks to search")
    #     else:
    #         for trackDict in self.trackArray:
    #             # handle case of A) only 1 tracked PRN  B) multiple tracked PRNs
    #             dictDim =  np.ndim(trackDict['PRN'])
    #             if dictDim == 1:
    #                 this_prn = trackDict['PRN'][0]
    #             elif dictDim == 2:
    #                 this_prn = trackDict['PRN'][0][0]
                
    #             if this_prn==prn: 
    #                 self.parseTrack(trackDict,do_plot)
    #                 break
    #             else:
    #                 continue 
        
    ## ---- PLOTTING -----
    def plot_gpsTrack(self,idx: int):
        GnssTrack.plot_hgTrack(self.gpsTracks[idx])
    def plot_geoTrack(self,idx):
        GnssTrack.plot_hgTrack(self.geoTracks[idx])       
    def plot_allGps(self,):
        for idx, gpsTrack in enumerate(self.gpsTracks):
            print("plotting %d" % idx)
            GnssTrack.plot_hgTrack(gpsTrack)
    def plot_allGeo(self,): 
        for idx, geoTrack in enumerate(self.geoTracks):
            print("plotting %d" % idx)
            GnssTrack.plot_hgTrack(geoTrack)       
    
    @staticmethod
    def plot_hgTrack(hgTrack: dict):
        time_s = hgTrack['time_s']
        prn = hgTrack['prn']
        data_I = hgTrack['data_I']
        data_Q = hgTrack['data_Q']
        dll = hgTrack['dll']
        pll = hgTrack['pll']
        carrier_lock = hgTrack['carrier_lock']
        rem_code_phase_sample = hgTrack['rem_code_phase_sample']
        acc_carrier_phase =  hgTrack['acc_carrier_phase']
        
        print("Plot Tracking of PRN %d" % prn)
            
        fig2, ax = plt.subplot_mosaic([['tl','tr'], ['ml','mr'], ['bl','br']], constrained_layout=True)
        ax['tl'].plot(data_I, data_Q, '.')
        ax['tl'].set_xlabel('I Data')
        ax['tl'].set_ylabel('Q Data')
        ax['tl'].set_title("Constellation Diagram")
        
        ax['tr'].plot(time_s, carrier_lock,)
        # ax['tr'].set_xlabel('Time (s)')
        ax['tr'].set_ylabel('Carrier Lock')
        ax['tr'].set_title("PRN %d Carrier Lock" % prn)
                    
        ax['ml'].plot(time_s, pll)
        ax['ml'].set_xlabel('Time (s)')
        ax['ml'].set_ylabel('Amplitude')
        ax['ml'].set_title('Filtered PLL Discrim')
    
        ax['mr'].plot(time_s, dll)
        ax['mr'].set_xlabel('Time (s)')
        ax['mr'].set_ylabel('Amplitude')
        ax['mr'].set_title('Filtered DLL Discrim')

        ax['bl'].plot(time_s, acc_carrier_phase)
        ax['bl'].set_title('Accum Carrier Phase')
        ax['bl'].set_ylabel('Phase (rad)')
        ax['bl'].set_xlabel('Time (s)')
        
        ax['br'].plot(time_s, rem_code_phase_sample)
        ax['br'].set_title('Remaining Code Phase')
        ax['br'].set_ylabel('Phase (sample)')
        ax['br'].set_xlabel('Time (s)')
    
    ## ----------- UTILITIES ------------- ##
    def printer(self, strg: str , force: bool):
        if self.debugLvl > 1 or force:
            print("GNSSTrack::%s :: %s" % (self.name, strg))
     

# %% example of new tracker stuff
# dr_path = '/home/darren/src/gnss-sdr/data/'
# fname_sbas = 'sbas/mini_0718_4m_bruce_lna_t2'  # old way
# fname_multi = 'sbas/multi/mini_0718_4m_bruce_lna_t2'
# fname = fname_multi
# track_trial = GnssTrack('trialB',data_path= dr_path + fname)
# track_trial.plot_allGeo()   
# track_trial.plot_allGps()

# %%  new GEO + GPS stuff  7/26
dr_path = '/home/darren/src/gnss-sdr/data/sbas/multi/'

t1 = 'sky_0816_20s.dat'
t2 = 'sky_0818_60s'
t3 = 'sky_0821_60s.dat'
t4 = 'sky_0823_60s'
t5 = 'sky_0832_60s'
files = [t1, t2, t3, t4, t5]
files_short = [t3, t4,]

tracks = []
for a_file in files_short:
    
    dPath = dr_path + a_file
    a_track = GnssTrack(data_path=dPath)
    tracks.append(a_track)
    
# %% do work on the tracks

for a_track in tracks:
    # a_track.plot_allGeo()
    a_track.plot_allGps()

plt.show()
print("grabTracks.py end\n")

# %%
