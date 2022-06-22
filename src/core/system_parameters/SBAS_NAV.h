/*!
 * \file SBAS_NAV.h
 * \brief  Defines parameters for SBAS NAV message
 * \author Darren Reis, HG 2022
 *
 * -----------------------------------------------------------------------------
 *
 * GNSS-SDR is a Global Navigation Satellite System software-defined receiver.
 * This file is part of GNSS-SDR.
 *
 * Copyright (C) 2010-2020  (see AUTHORS file for a list of contributors)
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * -----------------------------------------------------------------------------
 */


#ifndef GNSS_SDR_SBAS_NAV_H
#define GNSS_SDR_SBAS_NAV_H

#include "MATH_CONSTANTS.h"
#include <cstdint>
#include <utility>  // std::pair
#include <vector>

/** \addtogroup Core
 * \{ */
/** \addtogroup System_Parameters
 * \{ */


// SBAS NAVIGATION MESSAGE STRUCTURE
// NAVIGATION MESSAGE FIELDS POSITIONS (from FAA-E-2892)

constexpr int32_t SBAS_DATA_PAGE_BITS = 250;

// common to all messages

const std::vector<std::pair<int32_t, int32_t> > SBAS_PREAMBLE({{0, 8}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_MSG_TYPE({{9, 6}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_CRC({{227, 14}});

// MESSAGE TYPE 1 (PRN Mask)
const std::vector<std::pair<int32_t, int32_t> > SBAS_PRN_MASK({{15, 210}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_PRN_IODP({{15+210, 2}});


// MESSAGE TYPE 2-5 (Fast Corrections)
const std::vector<std::pair<int32_t, int32_t> > SBAS_FC_IODF({{15, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_FC_IODP({{17, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_FC({{19,13*12}}); // part a 
const std::vector<std::pair<int32_t, int32_t> > SBAS_FC_UDREI({{19+13*12,13*4}}); // part b .


// MESSAGE TYPE 6 (Integrity)
const std::vector<std::pair<int32_t, int32_t> > SBAS_INT_IODF2({{15, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_INT_IODF3({{17, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_INT_IODF4({{19, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_INT_IODF5({{21, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_INT_UDREI({{23, 51*4}});

// MESSAGE TYPE 7 (Degradation Factor)
const std::vector<std::pair<int32_t, int32_t> > SBAS_DF_SYSLAT({{15, 4}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_DF_IODP({{19, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_DF_SPARE({{21, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_DF_DFI({{23, 51*4}});

// MESSAGE TYPE 9 (Sat Nav)
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_RES({{15, 8}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_TGEO({{23, 13}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_URA({{36, 4}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_XG({{40, 30}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_YG({{70, 30}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_ZG({{100, 25}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_XG_DOT({{125, 17}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_YG_DOT({{145, 17}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_ZG_DOT({{162, 18}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_XG_DDOT({{180, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_YG_DDOT({{190, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_ZG_DDOT({{200, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_A_GF0({{210, 12}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_SAT_A_GF1({{222, 8}});  

// MESSAGE TYPE 10 (UDRE Degradation)

const std::vector<std::pair<int32_t, int32_t> > SBAS_UD_BRRC({{15, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_UD_C_LTC_LSB({{25, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_UD_C_LTC_V1({{35, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_UD_I_LTC_V1({{45, 9}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_UD_C_LTC_V1({{54, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_UD_I_LTC_V1({{64, 9}});

// MESSAGE TYPE 12 (UTC SBAS)

// MESSAGE TYPE 17 (GEO Almanac)
// this group repeats 2 more times
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_RESERVED({{15, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_PRN_ID({{17, 8}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_HEALTH({{25, 8}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_XGA({{33, 15}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_YGA({{48, 15}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_ZGA({{63, 9}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_XGA_DOT({{72, 3}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_YGA_DOT({{75, 3}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_ZGA_DOT({{78, 4}});
// no repeat on the next item
const std::vector<std::pair<int32_t, int32_t> > SBAS_GA_TOD({{82, 11}});

// MESSAGE TYPE 18 (Ionosphere Grid Mask)

// MESSAGE TYPE 24 (Mixed Corrections)
const std::vector<std::pair<int32_t, int32_t> > SBAS_MC_FC({{15, 6*12}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_MC_UDREI({{87, 6*4}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_MC_IODP({{111, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_MC_FC_ID({{113, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_MC_IODF({{115, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_MC_SPARE({{117, 4}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_MC_HALF_MESSAGE({{121, 106}});

// MESSAGE TYPE 26 (Ionosphere Correction)
const std::vector<std::pair<int32_t, int32_t> > SBAS_IC_BAND_ID({{15, 4}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_IC_BLOCK_ID({{19, 4}});
// the below repeats 15 times.  @TODO!
const std::vector<std::pair<int32_t, int32_t> > SBAS_IC_IGP_DELAY({{23, 9}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_IC_GIVEI({{32, 4}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_IC_IODI({{218, 2}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_IC_SPARE({{220, 7}});

// MESSAGE TYPE 28 (Ephem Cov)
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_IODP({{15, 2}});
// the below repeats 2 times.  @TODO
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_PRN_MASK({{17, 6}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_SCALE({{23, 3}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E11({{26, 9}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E22({{35, 9}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E33({{44, 9}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E44({{53, 9}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E12({{62, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E13({{72, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E14({{82, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E23({{92, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E24({{102, 10}});
const std::vector<std::pair<int32_t, int32_t> > SBAS_ECOV_E34({{112, 10}});

/** \} */
/** \} */
#endif  // SBAS_NAV_H
