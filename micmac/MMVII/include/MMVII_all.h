#ifndef _MMVII_ALL_H_
#define _MMVII_ALL_H_
/** \file MMVII_all.h
    \brief Contains all header of MMVII

  Try to put together files having something in common, not always easy ...
*/


// Header standar c++
#include "memory.h"
#include <memory>
#include <iostream>
#include <fstream>
#include <string>
#include <typeinfo>
#include <vector>
#include <list>
#include <ctime>
#include <chrono>
// #include <algorithm> => put it in file requiring it as it seem to slow down compilation
#include<boost/optional.hpp>


//========== LIB EXTEN==============


//===========================================
#include "MMVII_AllClassDeclare.h"
#include "MMVII_Error.h"
#include "MMVII_enums.h"
// Header MMVII
// #include "TypeNum.h"
#include "MMVII_DeclareCste.h"
#include "MMVII_Sys.h"
#include "MMVII_memory.h"
#include "MMVII_util_tpl.h"
#include "MMVII_nums.h"
#include "MMVII_util.h"



// Les class cPtxd, cPt1d, cPt2d
#include "MMVII_Ptxd.h"
#include "MMVII_Mappings.h"
#include "MMVII_Sensor.h"

// Les classe lies aux conversion vers des chaines, fichier ...
#include "MMVII_Stringifier.h"
#include "MMVII_Bench.h"
#include "cMMVII_Appli.h"


//  Classes for images manipulation

#include "MMVII_Images.h"


#include "MMVII_DeclareAllCmd.h"
// communication MMVII/MMv1

#include "MMVII_MMV1Compat.h"


#endif //  _MMVII_ALL_H_
