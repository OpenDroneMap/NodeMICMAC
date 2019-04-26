#include "include/MMVII_all.h"

namespace MMVII
{

template <> const std::string  & XMLTagSet<std::string> () {return TagSetOfName;}
template <> const std::string  & XMLTagSet<tNamePair>   () {return TagSetOfCpleName;}


template <> const std::string  & MMv1_XMLTagSet<std::string> () {return MMv1XmlTag_SetName;}
template <> const std::string  & MMv1_XMLTagSet<tNamePair> ()   {return MMv1XmlTag_RelName;}

/* =========================    STRING CONSTANTE  ========================= */

// XML TAG
    // V1 -  MicMac-v1  compatiblity 
const std::string  MMv1XmlTag_SetName = "ListOfName";
const std::string  MMv1XmlTag_RelName = "SauvegardeNamedRel";
    // V2
const std::string TagMMVIISerial = "MMVII_Serialization";
const std::string TagSetOfName = "SetOfName";
const std::string TagSetOfCpleName = "SetCpleOfName";

// const std::string TheMMVII_SysName => voir Utils/uti_sysdep.cpp
 
// Name of standard directories
const std::string TmpMMVIIDir    = "Tmp-2007-Dir/";
const std::string MMVIITestDir    = "MMVII-TestDir/";

// Name of common parameters
      // -- External
const std::string GOP_DirProj  = "DirProj";
const std::string GOP_NumVO    = "NumVOut";
const std::string GOP_Int0     = "FFI0";
const std::string GOP_Int1     = "FFI1";
const std::string GOP_StdOut   = "StdOut";
const std::string GOP_SeedRand = "SeedRand";
      // -- Internal
const std::string GIP_LevCall = "LevCall";
const std::string GIP_ShowAll = "ShowAll";


#if (THE_MACRO_MMVII_SYS == MMVII_SYS_L)
const char CharProctected = '\\';
#endif

const std::string  Bin2007 = "MMVII";

// User/Command
const   std::string MMVII_NONE = "NONE";


};

