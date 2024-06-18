''' python file to call the uhd tools to collect raw data from USRP
darren reis
07/06/22
'''

import argparse
import subprocess
import sys, os, shutil

class GrabUsrp():
        
    def __init__(self, fname=None, freq=1575.42, fs=4, dur=60, gain=50, typ='short', chan='B'):
        ''' Constructor '''
        if typ not in ['short', 'complex']:
            print("typ given %s, must be one of ['short', 'complex']" % typ)
            exit()

        script = "/usr/local/lib/uhd/examples/rx_samples_to_file"
        self.args = " --args \"type=b200\" --duration %d --freq %d --rate %d --ref external"  \
            " --type %s --gain %d " % (dur, freq*1e6, fs*1e6, typ, gain)
        self.args += "--file %s" % fname
        self.pick_ch(chan)
        
        result = subprocess.run(["bash", "-c", script + self.args], text=True)
        result.check_returncode()
        print("success load")

    def pick_ch(self, chan):
        # see "fwd_rtn.py set_subdev_spec() for uhd swig module method equivalent"
        if chan == 'A':
            # A: RX2
            self.args += " --subdev A:A"
        elif chan == 'B':
            # B: RX2
            self.args += " --subdev A:B"

if __name__ == "__main__":
    
    print(f"{__file__} startup\n")

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
    parser.add_argument('-c','--chan', action='store',  default='B',
                        choices=('A','B'), help='the subdevice channel, one of [A,B]')
    parser.add_argument('-t','--type', action='store', type=str, choices=('short','complex'),
                        default='short', help='the datatype to collection, one of [\'short\', \'complex\']')    
    
    # get arguments
    args = parser.parse_args(sys.argv[1:])
    
    if args.name is None:
        print(f"{__file__} requires a save name for file output")
        exit
    else:
        if not args.name.endswith('.dat'):
            print(f"{__file__} requires the save name with extension .dat")
            exit
            
    GrabUsrp(fname=args.name, freq=args.freq, gain=args.gain, dur=args.sec, chan=args.chan, typ=args.type)
    
    
    print(f"{__file__} finish\n")
