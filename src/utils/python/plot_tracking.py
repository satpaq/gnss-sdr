import h5py
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys, os, shutil

def handle_tracking():
    track_log_path = '/home/groundpaq/darren_space/gnss-sdr/data'

    filename = track_log_path + '/tracking_ch_0.mat';

    arrays = {}
    f = h5py.File(filename)
    for k, v in f.items():
        arrays[k] = np.array(v)

    print(len(arrays))
    print("end of tracking")

if __name__ == "__main__":
    
    print("plot_tracking.py startup\n")

    ## -- PARSER ----
    parser = argparse.ArgumentParser(description=''' 
    This script is a class for doing gnss-sdr work ''')
    
    # setup params
    parser.add_argument('-dt','--timestep', action='store', nargs=1, type=int,
                        default=312, help='the number of seconds between data')

    handle_tracking()