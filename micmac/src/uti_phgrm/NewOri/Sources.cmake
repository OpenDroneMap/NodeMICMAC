set(uti_phgrm_NewOri_Src_Files
    ${UTI_PHGRM_NEW_ORI}/TestNewOri.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_Appli.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_CpleIm.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_OneIm.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_NameManager.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_ProjPts.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_CombineCple.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_LinearCpleI.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_AmbigCpleI.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_GenTriplets.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_OldGenTriplets.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_PointsTriples.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_OptimTriplet.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_SolGlobInit.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_SolGlobInit_Build.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_SolGlob_PondApriori.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_DynFusPtsMul.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_Ellips.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_Hom1Im.cpp
    ${UTI_PHGRM_NEW_ORI}/cNewO_FicObs.cpp
    ${UTI_PHGRM_NEW_ORI}/GpsLoc.cpp
)


list( APPEND uti_phgrm_Src_Files
	${uti_phgrm_NewOri_Src_Files}
)


