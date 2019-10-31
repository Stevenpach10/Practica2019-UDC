/* ---------------------------------------------------
   FILE:     simParams.h
	AUTHOR:   Josh Bongard
	DATE:     October 5, 2000
	FUNCTION: This class contains all miscellaneous
				 data and functions for this simulation.
 -------------------------------------------------- */
#include "iostream"
#include "fstream"

#ifndef _SIM_PARAMS_H
#define _SIM_PARAMS_H

#include "matrix.h"

class SIM_PARAMS {

public:
	int		randSeed;
	int		numMutations;
	int		numHiddenNeurons;

	char 		tempFileName[200];
	char 		tausFileName[200];
	char 		weightsFileName[200];
	char 		omegasFileName[200];
	char 		sensorsFileName[200];
	char 		bodyFileName[200];
	char 		sensorFileName[200];

	time_t		startTime;

public:
	SIM_PARAMS(int argc, char **argv);
	~SIM_PARAMS(void);
	void   CloseDataFiles(void);
	void   DirectoryMake(char *dirName);
	void   FileCreate(char *fileName);
	void   FileDelete(char *fileName);
	int    FileExists(char *fileName);
	void   FileRename(char *src, char *dest);
	int    FlipCoin(void);
	ofstream *GetOutFile(char *fileName);
	double HoursSinceStart(void);
	void   ParseParameters(int argc, char **argv);
	double Rand(double min, double max);
	double RandGaussian(void);
	int    RandInt(int min, int max);
	double Scale(double value, double min1, double max1,
		         double min2, double max2);
	void   WaitForFile(char *fileName);
};

#endif
