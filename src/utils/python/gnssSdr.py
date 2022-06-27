from random import sample
import h5py
import numpy as np
import matplotlib.pyplot as plt
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

    def plot_acq(self,):
        # see https://gnss-sdr.org/docs/sp-blocks/acquisition/#plotting-results-with-matlaboctave


        acqArray = []
        for ch in self.chVec:
            filename = self.log_path + '/acq_1c_dump_G_1C_ch_%d_1_sat_1.mat' % ch
            acqDict = load_dumpMat(filename)
            acqArray.append(acqDict)
            
    def plot_observables(self, ):

        # see fields in https://gnss-sdr.org/docs/sp-blocks/observables/#binary-output
        obsArray = []
        for ch in self.chVec:
            filename = self.log_path + '/observ_ch_%d.mat' % ch
            obsDict = load_dumpMat(filename)
            obsArray.append(obsDict)

    def plot_tracking(self):
        # see field names in https://gnss-sdr.org/docs/sp-blocks/tracking/#plotting-results-with-matlaboctave
        
        samplingFreq = 3e6  # Hz
                
        ax = np.zeros_like(self.chVec)


        trackArray = []
        for ch in self.chVec:
            filename = self.log_path + '/tracking_ch_%d.mat' % ch
            trackDict = load_dumpMat(filename)
            trackArray.append(trackDict)


        if self.nChan == 1:
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
            for chIdx, ch in enumerate(self.chVec):
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

    l_path = '/home/groundpaq/darren_space/gnss-sdr/data'

    a_gnss = GNSS_SDR(nChan=1, log_path=l_path)

    a_gnss.plot_tracking()

    plt.show()
    print("plot_tracking.py end\n")