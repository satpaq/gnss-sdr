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
            self.in_fpath = '2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN/2013_04_04_GNSS_SIGNAL_at_CTTC_SPAIN.dat'
        else:
            if dat_path.endswith('.dat'):
                self.in_fpath = dat_path
            else:
                print("input file must be a .dat")
                exit
        
        workDir = os.getcwd()
        homeDir = os.path.dirname(workDir)
        self.homeDir = homeDir
        
        self.args = ''
        # set up command args
        try:
            self.set_conf_type(conf_typ)
            self.set_output_dir()
            self.set_log_file()
            self.set_dat_file()
            # self.set_std_out()
            self.handle_library_path()
        except NameError:
            exit()
        
            
        script = "gnss-sdr"
        cmd = script + self.args
        print("running:: %s" % cmd)
        result = subprocess.run(["bash", "-c", cmd], env=self.new_env, text=True)
        # various failure handling
        result.check_returncode()
        print("success gnss-sdr computation")

        # print("note right now, when this fails, you need to cd into /work, then do \n")
        # print("rm 1C_*")
        # print("rm S1_*")
    
    
    def set_conf_type(self,conf_typ):
        if conf_typ=='d':
            conf_file = 'gnss-sdr_GPS_L1_darren.conf'
        elif conf_typ=='s':
            conf_file = 'gnss-sdr_GPS_L1_spain.conf'
        elif conf_typ=='w':
            conf_file = 'gnss-sdr_GPS_L1_sbas.conf'
        elif conf_typ=='m':
            conf_file = 'gnss-sdr_GPS_L1_sbas_multi.conf'
        else:
            raise NameError("bad conf type given, %s" % conf_typ)
        
        self.conf_file = self.homeDir + '/work/' + conf_file
        self.dir_prefix = conf_file.split('_')[-1].split('.')[0]  # grab out the _NAME.conf
        self.args += ' --config_file=%s' % self.conf_file
                
    def set_output_dir(self,):
        ''' set up the path str for outputs '''
        rel_dir = "/data/sbas/" + self.dir_prefix + '/'
        self.out_dir = self.homeDir + rel_dir
        
        if (not os.path.isdir(self.out_dir)):
            # make dir if doesn't exist,
            os.makedirs(self.out_dir)
        else:
            #  clear and make it again
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

    def handle_library_path(self,):
        ''' handle the library path thing for boost '''
        new_env = os.environ.copy()
        blmckinley_lib = '/home/blmckinley/install/lib'
        new_env["LD_LIBRARY_PATH"] = ':' + blmckinley_lib
        self.new_env = new_env
        # overwrite the env
        # try:
        #     os.execv(sys.argv[0], sys.argv)
        # except Exception as e:
        #     sys.exit('EXCEPTION: Failed to Execute under modified environment, '+e)
        

if __name__ == "__main__":
    
    print("--- process_data.py startup\n")

    ## -- PARSER ----
    parser = argparse.ArgumentParser(description=''' 
    This script is a tool to simplify processing .dat output from uhd_collection ''')
    
    # setup params
    parser.add_argument('-f','--datFile', action='store', type=str,
                        default=None, help='the .dat file to process, with relative path')
    parser.add_argument('-c','--config', action='store', type=str,
                        default=None, help='the type of config to use, \'s\' for spain, \
                            \'d\' for darren, \'w\' for SBAS, \'m\' for multi ')
    
    # get arguments
    args = parser.parse_args(sys.argv[1:])
    
    
    if args.datFile is None:
        print("process_data requires a .dat file input\n")
        
    
    if args.config is None:
        print("process_data requires one of ['s', 'd', 'w'] to pick a .conf file\n")
        exit
    
        
    RunGnssSdr(conf_typ=args.config, dat_path=args.datFile, do_log=True)
    
    print("---- process_data.py finish\n")
