/*Header-MicMac-eLiSe-25/06/2007

    MicMac : Multi Image Correspondances par Methodes Automatiques de Correlation
    eLiSe  : ELements of an Image Software Environnement

    www.micmac.ign.fr

   
    Copyright : Institut Geographique National
    Author : Marc Pierrot Deseilligny
    Contributors : Gregoire Maillet, Didier Boldo.

[1] M. Pierrot-Deseilligny, N. Paparoditis.
    "A multiresolution and optimization-based image matching approach:
    An application to surface reconstruction from SPOT5-HRS stereo imagery."
    In IAPRS vol XXXVI-1/W41 in ISPRS Workshop On Topographic Mapping From Space
    (With Special Emphasis on Small Satellites), Ankara, Turquie, 02-2006.

[2] M. Pierrot-Deseilligny, "MicMac, un lociel de mise en correspondance
    d'images, adapte au contexte geograhique" to appears in 
    Bulletin d'information de l'Institut Geographique National, 2007.

Francais :

   MicMac est un logiciel de mise en correspondance d'image adapte 
   au contexte de recherche en information geographique. Il s'appuie sur
   la bibliotheque de manipulation d'image eLiSe. Il est distibue sous la
   licences Cecill-B.  Voir en bas de fichier et  http://www.cecill.info.


English :

    MicMac is an open source software specialized in image matching
    for research in geographic information. MicMac is built on the
    eLiSe image library. MicMac is governed by the  "Cecill-B licence".
    See below and http://www.cecill.info.

Header-MicMac-eLiSe-25/06/2007*/
#ifndef _EL_REGEX_H_
#define _EL_REGEX_H_

#include <string>
#include <vector>
#include <list>

#if ELISE_windows
	#include "win_regex.h"
#else
	#include <regex.h>
#endif




#include <assert.h>


 



#define InfRegex 1.2345e60

class cElRegex
{
    public :
       cElRegex(const std::string & aName,int aNbMatchMax,int aCFlag=REG_EXTENDED,bool CaseSensitive=true);
       bool IsOk() const;
       bool IsMatched() const;
       bool IsReplaced() const;
       const std::string & LastReplaced() const;
       const std::string & NameExpr() const;
       ~cElRegex();
       bool Match(const std::string &,int aCFlag=0) ;
       bool  Replace(const std::string & Motif) ;

       std::string KIemeExprPar(int aNum);
       double VNumKIemeExprPar(int aNum,bool Verif=true,double * aDefError = 0);


       // Interface bas niveau
       const std::vector<regmatch_t>  & VMatch() const;
       const std::string & Error() const;

       static cElRegex * AutomSurvey();
       static cElRegex * AutomUDS();  // Universite de savoie, provenance ??

    private :
       void AssertOk() const;
       void AssertIsMatched() const;
       void AssertIsReplaced() const;

       regex_t                  mAutom;
       std::vector<regmatch_t>  mVMatch;
       int                      mResCreate;
       int                      mResMatch;
       bool                     mOkReplace;
       std::string              mLastNameMatched;
       std::string              mLastReplace;
       std::string              mNameExpr;

       std::string              mError;
       bool                     mCaseSensitive;
};

std::list<cElRegex *> CompilePats(const  std::list<std::string> &);
bool AuMoinsUnMatch(const std::list<cElRegex *> &,const  std::string &);


typedef  cElRegex * cElRegex_Ptr;

  // Dans lib-eLiSe
extern std::string MatchAndReplace( cElRegex & anExpr,
                                    const std::string & aName,
                                   const std::string &aRepl);


std::vector<double> GetValsNumFromLineExprReg
                    (
                        cElRegex_Ptr &,
                        const std::string & aNameFile,
                        const std::string & aNameExpr,
                        const std::string & aVInd,
                        int * aPtrNbMatch = 0
                    );

std::string  GetStringFromLineExprReg
             (
                  cElRegex_Ptr & aReg,
                  const std::string & aNameFile,
                  const std::string & aNameExpr,
                  const std::string & aMotif,
                  int * aPtrNbMatch = 0
             );



// class pour memoriser le Nom, centre et orientation d'un fichier de trajecto
class  cLine_N_XYZ_WPK
{
    public :
       static std::vector<cLine_N_XYZ_WPK> 
              FromFile(   const cElRegex_Ptr &,
                          int *aNum,
                          const std::string & aLine,
                          bool aShowLinNonInterp
                      );
       static const double TheNoVal;
       std::string mName;
       Pt3dr       mXYZ;
       Pt3dr       mWPK;
       bool        mOK;
 
       cLine_N_XYZ_WPK(const cElRegex_Ptr &,int *aNum,const std::string & aLine);
};


#endif // _EL_REGEX_H_


/*Footer-MicMac-eLiSe-25/06/2007

Ce logiciel est un programme informatique servant à la mise en
correspondances d'images pour la reconstruction du relief.

Ce logiciel est régi par la licence CeCILL-B soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL-B telle que diffusée par le CEA, le CNRS et l'INRIA 
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant 
donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
pris connaissance de la licence CeCILL-B, et que vous en avez accepté les
termes.
Footer-MicMac-eLiSe-25/06/2007*/
