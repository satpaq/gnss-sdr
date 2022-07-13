/*!
 * \file dump_tools.cc
 * \brief  This class has utility functions for handling dumping
 * \author Darren Reis, 2022
 *      
 *  eventually we could have a Saver class that has methods for storing away
 *  items to .dat or .mat classes.  It would handle the directories, file naming, etc.
 * 
 *  -----------------------------------------------------------------------------
 */


#include "gnss_sdr_create_directory.h"
#include "gnss_sdr_filesystem.h"
#include <iostream>   // for cout, cerr

std::string makeDumpFile(std::string dir, std::string name){
    std::string dump_path;

    if (dir.empty())
    {   
        // name has folder delimiters
        if (name.find_last_of('/') != std::string::npos)
            {
                std::string dump_filename_ = name.substr(name.find_last_of('/') + 1);
                dump_path = name.substr(0, name.find_last_of('/'));
                name = dump_filename_;
            }    
        else
            {
                dump_path = std::string(".");
            }
        }
    else
        dump_path = dir;
    
    if (name.empty())
        {
           name = "trk_channel_";                    
        }
    // remove extension if any
    if (name.substr(1).find_last_of('.') != std::string::npos)
        {
            name = name.substr(0, name.find_last_of('.'));
        }

    name = dump_path + fs::path::preferred_separator + name;
    return name;
}


// create directory if needed
bool makeDumpDir(std::string dir){
    if (!gnss_sdr_create_directory(dir))
        {
            std::cerr << "GNSS-SDR cannot create dump files for the tracking block. "
            "Did you remeber to mkdir the folder?\n";
            return false;
        }
    else
        {
            return true;
        }    
}
