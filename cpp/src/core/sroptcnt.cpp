/************************************************************************//**
 * File: sroptcnt.cpp
 * Description: Optical element: Container
 * Project: Synchrotron Radiation Workshop
 * First release: 2000
 *
 * Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
 * All Rights Reserved
 *
 * @author O.Chubar, P.Elleaume
 * @version 1.0
 ***************************************************************************/

#include "sroptcnt.h"
#include "sroptdrf.h"
#include "sroptapt.h"
#include "sroptfoc.h"
#include "sroptzp.h"
#include "sroptwgr.h"
#include "sroptgrat.h"
#include "sroptgtr.h"
#include "sropthck.h"
#include "auxparse.h"
#include "srwlib.h"

//*************************************************************************

extern int (*pgOptElemGetInfByNameFunc)(const char* sNameOptElem, char** pDescrStr, int* pLenDescr, void*);

//*************************************************************************

srTCompositeOptElem::srTCompositeOptElem(srTStringVect* pElemInfo, srTSRWRadStructAccessData* pRad)
{
	int AmOfMembers = (int)pElemInfo->size() - 1;

	//srTSend Send;
	int result = 0;

	const int maxStrLen = 256; //to tune
	const int maxNumParam = 200; //to tune
	char strAuxBuf[maxStrLen*maxNumParam];
	char *pDescrStr[maxNumParam];
	char *tStrAuxBuf = strAuxBuf; //**tDescrStr = pDescrStr;
	for(int i=0; i<maxNumParam; i++)
	{
		*tStrAuxBuf = '\0';
		pDescrStr[i] = tStrAuxBuf;
		tStrAuxBuf += maxStrLen;
	}
	int LenDescr = 0;
	srTDataMD OptElemNumData;

	for(int i=1; i<=AmOfMembers; i++)
	{
		char* MemberID = (*pElemInfo)[i];
		srTStringVect MemberInfo;

		//if(result = Send.GetVectorOfStrings(MemberID, &MemberInfo)) { ErrorCode = result; return;}

		OptElemNumData.pData = 0; //add other marks?
		if(result = (*pgOptElemGetInfByNameFunc)(MemberID, pDescrStr, &LenDescr, &OptElemNumData)) { ErrorCode = result; return;}
		CAuxParse::StringArr2VectCStr(pDescrStr, LenDescr, MemberInfo);

		srTGenOptElemHndl OptElemHndl;
		//if(result = OptElemSummary.SetupOpticalElement(&MemberInfo, OptElemHndl, pRad)) { ErrorCode = result; return;}
		//if(result = srTOptElemSummary::SetupOpticalElement(&MemberInfo, OptElemHndl, pRad)) { ErrorCode = result; return;}
		if(result = SetupOpticalElement(&MemberInfo, &OptElemNumData, pRad, OptElemHndl)) { ErrorCode = result; return;}

		AddOptElemBack(OptElemHndl);

		//for(int k=0; k<(int)(MemberInfo.size()); k++)
		//{
		//	char* aStr = MemberInfo[k];
		//	if(aStr != 0) delete[] aStr;
		//}
	}
}

//*************************************************************************

srTCompositeOptElem::srTCompositeOptElem(const SRWLOptC& opt)
{//to add more optical elements
	void **t_arOpt = opt.arOpt;
	char **t_arOptTypes = opt.arOptTypes;
	if((opt.nElem <= 0) || (t_arOpt == 0) || (t_arOptTypes == 0)) throw UNKNOWN_OPTICAL_ELEMENT;

	double **t_arProp = opt.arProp;
	//srTRadResize propResLast;
	//bool propResWasSet = false;

	for(int i=0; i<=opt.nElem; i++)
	{
		srTGenOptElem *pOptElem=0;
		if(i < opt.nElem)
		{
			if((*t_arOpt) == 0) throw UNKNOWN_OPTICAL_ELEMENT;
			char *sType = *t_arOptTypes;
			if(strcmp(sType, "drift") == 0)
			{
				pOptElem = new srTDriftSpace(((SRWLOptD*)(*t_arOpt))->L); 
			}
			else if((strcmp(sType, "aperture") == 0) || (strcmp(sType, "obstacle") == 0))
			{
				SRWLOptA *p = (SRWLOptA*)(*t_arOpt);
				if((p->ap_or_ob == 'a') || (p->ap_or_ob == 'A'))
				{
					if(p->shape == 'r') pOptElem = new srTRectAperture(p->Dx, p->Dy, p->x, p->y);
					else if(p->shape == 'c') pOptElem = new srTCircAperture(p->Dx, p->x, p->y);
				}
				else if((p->ap_or_ob == 'o') || (p->ap_or_ob == 'O'))
				{
					if(p->shape == 'r') pOptElem = new srTRectObstacle(p->Dx, p->Dy, p->x, p->y);
					else if(p->shape == 'c') pOptElem = new srTCircObstacle(p->Dx, p->x, p->y);
				}
				else throw UNKNOWN_OPTICAL_ELEMENT;
			}
			else if(strcmp(sType, "lens") == 0)
			{
				SRWLOptL *p = (SRWLOptL*)(*t_arOpt);
				pOptElem = new srTThinLens(p->Fx, p->Fy, p->x, p->y);
			}
			else if((strcmp(sType, "zp") == 0) || (strcmp(sType, "ZP") == 0))
			{
				SRWLOptZP *p = (SRWLOptZP*)(*t_arOpt);
				pOptElem = new srTZonePlate(p->nZones, p->rn, p->thick, p->atLen1, p->atLen2, p->delta1, p->delta2, p->x, p->y);
			}
			else if(strcmp(sType, "waveguide") == 0)
			{
				SRWLOptWG *p = (SRWLOptWG*)(*t_arOpt);
				pOptElem = new srTWaveguideRect(p->L, p->Dx, p->Dy, p->x, p->y); 
			}
			else if(strcmp(sType, "grating") == 0)
			{
				SRWLOptG *p = (SRWLOptG*)(*t_arOpt);
				pOptElem = new srTGrating(p->grDen, p->disPl, p->ang, p->m, p->refl);
			}
			else if(strcmp(sType, "transmission") == 0)
			{
				pOptElem = new srTGenTransmission(*((SRWLOptT*)(*t_arOpt)));
			}
			else if(strcmp(sType, "mirror: ellipsoid") == 0)
			{
				pOptElem = new srTMirrorEllipsoid(*((SRWLOptMirEl*)(*t_arOpt)));
			}
			else if(strcmp(sType, "mirror: toroid") == 0)
			{
				pOptElem = new srTMirrorToroid(*((SRWLOptMirTor*)(*t_arOpt)));
			}

			else if(strcmp(sType, "container") == 0)
			{
				pOptElem = new srTCompositeOptElem(*((SRWLOptC*)(*t_arOpt)));
			}
			else throw UNKNOWN_OPTICAL_ELEMENT;
		}
		if(pOptElem != 0)
		{
			CSmartPtr<CGenObject> hObj(pOptElem);
			AddOptElemBack(hObj);
		}
		if((opt.arProp != 0) && ((pOptElem != 0) || (i == opt.nElem)))
		{
			srTRadResize propRes; //with all default parameters
			//if((i > 0) && (i < opt.nElem) && (i >= opt.nProp) && propResWasSet) propRes = propResLast;
			if(i < opt.nProp)
			{
				double *t_pr = *t_arProp;
				propRes.propAutoResizeBefore((int)(t_pr[0]));
				propRes.propAutoResizeAfter((int)(t_pr[1]));
				propRes.PropAutoPrec = t_pr[2];
				propRes.propAllowUnderSamp((int)(t_pr[3]));
				propRes.useOtherSideFFT((int)(t_pr[4]));
				propRes.pxm = t_pr[5];
				propRes.pxd = t_pr[6];
				propRes.pzm = t_pr[7];
				propRes.pzd = t_pr[8];
				propRes.ShiftTypeBeforeRes = (char)t_pr[9];
				propRes.xCenShift = t_pr[10];
				propRes.zCenShift = t_pr[11];
			}

			GenOptElemPropResizeVect.push_back(propRes); //define instructions for propagation/resizing
			//propResLast = propRes;
			//propResWasSet = true;
		}
		t_arOpt++;
		t_arOptTypes++;
		t_arProp++;
	}
}

//*************************************************************************

int srTCompositeOptElem::PropagateRadiationTest(srTSRWRadStructAccessData* pInRadAccessData, srTSRWRadStructAccessData* pOutRadAccessData)
{
	int result;
	int AmOfDrifts = 0;
	for(srTGenOptElemHndlList::iterator iter = GenOptElemList.begin(); iter != GenOptElemList.end(); ++iter)
	{
		srTDriftSpace* pDrift = dynamic_cast<srTDriftSpace*>((*iter).rep);
		if(pDrift != NULL) AmOfDrifts++;
	}
	
	if(AmOfDrifts > 1) return PROP_TEST_CONSTRAINTS;
	else 
	{
		if(AmOfDrifts == 1)
		{
			srTGenOptElemHndlList::iterator pLast = GenOptElemList.end(); pLast--;
			srTDriftSpace* pDrift = dynamic_cast<srTDriftSpace*>((*pLast).rep);
			if(pDrift == NULL) return PROP_TEST_CONSTRAINTS;
		}

		for(srTGenOptElemHndlList::iterator iter = GenOptElemList.begin(); iter != GenOptElemList.end(); ++iter)
			//if(result = ((*iter).rep)->PropagateRadiationTest(pInRadAccessData, pOutRadAccessData)) return result;
			if(result = ((srTGenOptElem*)((*iter).rep))->PropagateRadiationTest(pInRadAccessData, pOutRadAccessData)) return result;
	}
	return 0;
}

//*************************************************************************

int srTCompositeOptElem::PropagateRadiationGuided(srTSRWRadStructAccessData& wfr)
{
	int numElem = (int)GenOptElemList.size();
	int numResizeInst = (int)GenOptElemPropResizeVect.size();
	const double tolRes = 1.e-04;
	int res = 0, elemCount = 0;
	for(srTGenOptElemHndlList::iterator it = GenOptElemList.begin(); it != GenOptElemList.end(); ++it)
	{
		int methNo = 0;
		int useResizeBefore = 0;
		int useResizeAfter = 0;
		double precFact = 1.;
		double underSampThresh = 0.5; //not user
		char analTreatment = 0;

		if(elemCount < numResizeInst)
		{
			srTRadResize &curPropResizeInst = GenOptElemPropResizeVect[elemCount];
			useResizeBefore = curPropResizeInst.propAutoResizeBefore();
			useResizeAfter = curPropResizeInst.propAutoResizeAfter();
			if(useResizeBefore || useResizeAfter) methNo = 2;

			precFact = curPropResizeInst.PropAutoPrec;
			analTreatment = curPropResizeInst.propAllowUnderSamp();

			//TO IMPLEMENT: eventual shift of wavefront before resizing!!!

			if((::fabs(curPropResizeInst.pxd - 1.) > tolRes) || (::fabs(curPropResizeInst.pxm - 1.) > tolRes) ||
			   (::fabs(curPropResizeInst.pzd - 1.) > tolRes) || (::fabs(curPropResizeInst.pzm - 1.) > tolRes))
				if(res = RadResizeGen(wfr, curPropResizeInst)) return res;
		}

		srTParPrecWfrPropag precParWfrPropag(methNo, useResizeBefore, useResizeAfter, precFact, underSampThresh, analTreatment);
		srTRadResizeVect auxResizeVect;
		if(res = ((srTGenOptElem*)(it->rep))->PropagateRadiation(&wfr, precParWfrPropag, auxResizeVect)) return res;
		//maybe to use "PropagateRadiationGuided" for srTCompositeOptElem?

		elemCount++;
	}
	if(elemCount < numResizeInst)
	{//post-resize
		//TO IMPLEMENT: eventual shift of wavefront before resizing!!!

		srTRadResize &postResize = GenOptElemPropResizeVect[elemCount];
		if((::fabs(postResize.pxd - 1.) > tolRes) || (::fabs(postResize.pxm - 1.) > tolRes) ||
		   (::fabs(postResize.pzd - 1.) > tolRes) || (::fabs(postResize.pzm - 1.) > tolRes))
			if(res = RadResizeGen(wfr, postResize)) return res;
	}
	return 0;
}

//*************************************************************************
