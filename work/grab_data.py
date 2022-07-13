''' python file to grab the uhd data for gnss-sdr
darren reis
07/06/22
'''

import argparse
import subprocess
import sys, os, shutil

class GrabGnssSdr():
        
    def __init__(self, fname=None, freq=1575.42, fs=4, dur=60, gain=50, typ='short',):
        ''' Constructor '''
        
        script = "/usr/lib/uhd/examples/rx_samples_to_file"
        args = " --args \"type=b200\" --duration %d --freq %d --rate %d --ref external"  \
            " --type short --gain %d " % (dur, freq*1e6, fs*1e6, gain)
        args += "--file %s" % fname
        
        result = subprocess.run(["bash", "-c", script + args], text=True)
        result.check_returncode()
        print("success load")


if __name__ == "__main__":
    
    print("grab_data.py startup\n")

    ## -- PARSER ----
    parser = argparse.ArgumentParser(description=''' 
    This script is a tool to simplify grabbing uhd data ''')
    
    # setup params
    parser.add_argument('-n','--name', action='store', type=str,
                        default=None, help='the name of the collection, with relative path ' \
                        'as \"../work/FILE.dat\"')
    parser.add_argument('-f','--freq', action='store',  type=float,
                        default=1575.42, help='the center freq of the collection, in MHz')
    parser.add_argument('-fs','--sampFreq', action='store',  type=float,
                        default=4.0, help='the sammple freq, in MHz')
    parser.add_argument('-g','--gain', action='store', type=int,
                        default=50, help='the gain of the collection, default to 50')
    parser.add_argument('-s','--sec', action='store', type=int,
                        default=20, help='the collection duration (s), default to 20')
    
    # get arguments
    args = parser.parse_args(sys.argv[1:])
    
    if args.name is None:
        print("grab_data requires a save name for file output")
        exit
    else:
        if not args.name.endswith('.dat'):
            print("grab_data requires the save name with extension .dat")
            exit
            
    GrabGnssSdr(fname=args.name, freq=args.freq, gain=args.gain, dur=args.sec)
    
    
    print("grab_data.py finish\n")