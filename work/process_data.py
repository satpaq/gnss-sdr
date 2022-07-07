''' python file to run the processing parts of gnss-sdr; run in the /work folder
darren reis
07/06/22
'''

import argparse
import subprocess
import sys, os, shutil

class RunGnssSdr():
        
    def __init__(self, conf_typ, dat_path, do_log=False):
        ''' Constructor '''
        # defualt case: output IO to shell, not log file
        self.do_log = do_log
        
        if conf_typ=='s':
            self.in_fpath = '/home/groundpaq/darren_space/gnss-sdr/work/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.dat'
        else:
            if dat_path.endswith('.dat'):
                self.in_fpath = dat_path
            else:
                print("input file must be a .dat")
                exit
        
        
        self.args = ''
        # set up command args
        self.set_conf_type(conf_typ)
        self.set_output_dir()
        self.set_log_file()
        self.set_dat_file()
        # and lastly
        self.set_std_out()
        
        script = "gnss-sdr"
        cmd = script # + self.args
        print("running:: %s" % cmd)
        result = subprocess.run(["bash", "-c", cmd], text=True)
        result.check_returncode()
        print("success gnss-sdr computation")

    
    
    def set_conf_type(self,conf_typ):
        if conf_typ=='d':
            conf_file = 'gnss-sdr_GPS_L1_darren.conf'
        elif conf_typ=='s':
            conf_file = 'gnss-sdr_GPS_L1_spain.conf'
            
        elif conf_typ=='w':
            conf_file = 'gnss-sdr_GPS_L1_sbas.conf'
        else:
            print("bad conf type given, quitting")
            exit
        self.conf_file = conf_file
        self.dir_prefix = conf_file.split('_')[-1].split('.')[0]  # grab out the _NAME.conf
        self.args += ' --config_file=%s' % self.conf_file
                
    def set_output_dir(self,):
        ''' set up the path str for outputs '''
        self.out_dir = "../data/" + self.dir_prefix + '/' + self.in_fpath.split(".")[0] + '/'
        # make dir if doesn't exist, else clear and make it again
        if (not os.path.isdir(self.out_dir)):
            os.makedirs(self.out_dir)
        else:
            subprocess.run(["rm", "-rf", self.out_dir])
            os.makedirs(self.out_dir)
        
        # schema is "../data/<type>/<fname>/"
            
    def set_log_file(self,):
        ''' set up the filename of the log files, inside the output_dir'''
        if self.do_log:
            self.args += ' --log_dir=%s' % self.out_dir 
    def set_dat_file(self,):
        ''' set up the loaded dat file'''
        self.args += ' --signal_source=%s' % self.in_fpath 

    def set_std_out(self,):
        ''' set up where the output file should go; this must go last'''
        self.args += ' -> %sstd.OUT' % self.out_dir


if __name__ == "__main__":
    
    print("--- process_data.py startup\n")

    ## -- PARSER ----
    parser = argparse.ArgumentParser(description=''' 
    This script is a tool to simplify processing .dat output from uhd_collection ''')
    
    # setup params
    parser.add_argument('-f','--datFile', action='store', type=str,
                        default=None, help='the .dat file to process, with relative path')
    parser.add_argument('-c','--config', action='store', type=str,
                        default=None, help='the type of config to use, \'s\' for spain, \'d\' for darren')
    
    # get arguments
    args = parser.parse_args(sys.argv[1:])
    
    if args.datFile is None:
        print("process_data requires a .dat file input\n")
        
    
    if args.config is None:
        print("process_data requires one of ['s', 'd', 'w'] to pick a .conf file\n")
        exit
    
        
    RunGnssSdr(conf_typ=args.config, dat_path=args.datFile,)
    
    print("---- process_data.py finish\n")
