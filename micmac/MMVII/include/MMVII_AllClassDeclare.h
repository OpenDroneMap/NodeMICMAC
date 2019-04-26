#ifndef  _MMVII_AllClassDeclare_H_
#define  _MMVII_AllClassDeclare_H_

namespace MMVII
{


/** \file MMVII_AllClassDeclare.h
    \brief Contains declaration  of all class

   As sooner or later many class require a forrward declaration,
 I think it's more readable to systematically declare everything
 here.

*/

enum class eTyUEr;

// MMVII_memory.h :  Memory

class  cMemState; // Memory state
class  cMemManager; // Allocator/desallocator tracking memory state
class  cMemCheck;   // Class calling cMemManager for allocation
template<class Type> class cGestObjetEmpruntable;


// MMVII_util.h :  Util
class cCarLookUpTable;
class cMMVII_Ofs ;
class cMMVII_Ifs ;

// MMVII_util_tpl.h

template <class Type> class cExtSet ;
template <class Type> class cSelector ;
template <class Type> class cDataSelector ;
template <class Type> class cOrderedPair ;

typedef cSelector<std::string>      tNameSelector;
typedef cExtSet<std::string>        tNameSet;
typedef cOrderedPair<std::string>   tNamePair; ///< Order does not matter
typedef std::pair<std::string,std::string>  tNameOCple;  ///< Order matters
typedef cExtSet<tNamePair>          tNameRel;



// MMVII_Ptxd.h
template <class Type,const int Dim> class cPtxd;

// MMVII_Bench.h

// cMMVII_Appli.h
// class cSetName;
class cArgMMVII_Appli;
class cSpecMMVII_Appli;
class cMMVII_Ap_NameManip;
class cMMVII_Ap_CPU;
class cMMVII_Appli ;

// MMVII_Stringifier.h

class  cSpecOneArgCL2007 ;
class cCollecSpecArg2007;

class cAuxAr2007;
class cAr2007;


};

#endif  //  _MMVII_AllClassDeclare_H_
