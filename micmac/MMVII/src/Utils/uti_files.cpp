#include "include/MMVII_all.h"

namespace MMVII
{

template<class Type> std::unique_ptr<Type>  NNfs(const std::string & aNameFile,const std::string & aMode,const std::string & aMes)
{
    std::unique_ptr<Type> aRes (new Type(aNameFile));

    if (!aRes->good())
    {
       MMVII_INTERNAL_ASSERT_user(eTyUEr::eOpenFile,"Cannot open file : "  + aNameFile + " ,Mode=" + aMode+  " ,context=" + aMes);
    }

    return aRes;
}


std::unique_ptr<std::ifstream>  NNIfs(const std::string & aNameFile,const std::string aMes)
{
   return NNfs<std::ifstream>(aNameFile,"READ",aMes);
}
std::unique_ptr<std::ofstream>  NNOfs(const std::string & aNameFile,const std::string aMes)
{
   return NNfs<std::ofstream>(aNameFile,"WRITE",aMes);
}

/*=============================================*/
/*                                             */
/*            cMMVII_Ofs                       */
/*                                             */
/*=============================================*/


cMMVII_Ofs::cMMVII_Ofs(const std::string & aName,bool ModeAppend) :
   mOfs  (aName,ModeAppend ? std::ios_base::app : std::ios_base::out),
   mName (aName)
{
    if (!mOfs.good())
    {
       MMVII_INTERNAL_ASSERT_user(eTyUEr::eOpenFile,"Cannot open file : "  + mName + " in mode write");
    }
}

const std::string &   cMMVII_Ofs::Name() const
{
   return mName;
}

std::ofstream & cMMVII_Ofs::Ofs() 
{
#if (The_MMVII_DebugLevel>=The_MMVII_DebugLevel_InternalError_tiny)
   if (!mOfs.good())
   {
       MMVII_INTERNAL_ASSERT_user(eTyUEr::eWriteFile,"Bad file for "+mName);
   }
#endif
   return mOfs;
}


void cMMVII_Ofs::VoidWrite(const void * aPtr,size_t aNb) 
{ 
#if (The_MMVII_DebugLevel>=The_MMVII_DebugLevel_InternalError_tiny)
   std::streampos aPos0 = mOfs.tellp();
#endif
   mOfs.write(static_cast<const char *>(aPtr),aNb); 
#if (The_MMVII_DebugLevel>=The_MMVII_DebugLevel_InternalError_tiny)
    bool Ok = mOfs.tellp() == (aPos0+std::streampos(aNb));
    if (!Ok)
    {
       MMVII_INTERNAL_ASSERT_tiny
       (
           false,
           std::string("Error in write for file ") + mName
       );
    }
#endif
}

void cMMVII_Ofs::Write(const int & aVal)    { VoidWrite(&aVal,sizeof(aVal)); }
void cMMVII_Ofs::Write(const double & aVal) { VoidWrite(&aVal,sizeof(aVal)); }
void cMMVII_Ofs::Write(const size_t & aVal) { VoidWrite(&aVal,sizeof(aVal)); }


void cMMVII_Ofs::Write(const std::string & aVal) 
{ 
   size_t aSz = aVal.size();
   Write(aSz);
   VoidWrite(aVal.c_str(),aSz);
}

/*=============================================*/
/*                                             */
/*            cMMVII_Ifs                       */
/*                                             */
/*=============================================*/


cMMVII_Ifs::cMMVII_Ifs(const std::string & aName) :
   mIfs  (aName),
   mName (aName)
{
    if (!mIfs.good())
    {
       MMVII_INTERNAL_ASSERT_user(eTyUEr::eOpenFile,"Cannot open file : "  + mName + " in mode read");
    }
}

const std::string &   cMMVII_Ifs::Name() const
{
   return mName;
}

std::ifstream & cMMVII_Ifs::Ifs() 
{
#if (The_MMVII_DebugLevel>=The_MMVII_DebugLevel_InternalError_tiny)
   if (!mIfs.good())
   {
       MMVII_INTERNAL_ASSERT_user(eTyUEr::eReadFile,"Bad file for "+mName);
   }
#endif
   return mIfs;
}


void cMMVII_Ifs::VoidRead(void * aPtr,size_t aNb) 
{ 
#if (The_MMVII_DebugLevel>=The_MMVII_DebugLevel_InternalError_tiny)
   std::streampos aPos0 = mIfs.tellg();
#endif
   mIfs.read(static_cast<char *>(aPtr),aNb); 
#if (The_MMVII_DebugLevel>=The_MMVII_DebugLevel_InternalError_tiny)
    bool Ok = mIfs.tellg() == (aPos0+std::streampos(aNb));
    if (!Ok)
    {
       MMVII_INTERNAL_ASSERT_tiny
       (
           false,
           std::string("Error in write for file ") + mName
       );
    }
#endif
}

void cMMVII_Ifs::Read(int & aVal)    { VoidRead(&aVal,sizeof(aVal)); }
void cMMVII_Ifs::Read(double & aVal) { VoidRead(&aVal,sizeof(aVal)); }
void cMMVII_Ifs::Read(size_t & aVal) { VoidRead(&aVal,sizeof(aVal)); }

void cMMVII_Ifs::Read(std::string & aVal )
{ 
   size_t aSz = TplRead<size_t>();
   aVal.resize(aSz);
   VoidRead(const_cast<char *>(aVal.c_str()),aSz);
}


};

