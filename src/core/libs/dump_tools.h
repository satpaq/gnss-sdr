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

#ifndef DUMP_TOOLS_H
#define DUMP_TOOLS_H

/** \addtogroup Core
 * \{ */
/** \addtogroup Core_Receiver_Library core_libs
 * \{ */

#include <fstream>                            // for ofstream
#include <string>                             // for string

std::string makeDumpFile(std::string dir, std::string name);
bool makeDumpDir(std::string dir);

/** \} */
/** \} */
#endif  // DUMP_TOOLS_H