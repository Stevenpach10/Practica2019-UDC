/* ---------------------------------------------------
   FILE:     simParams.cpp
	AUTHOR:   Josh Bongard
	DATE:     October 5, 2000
	FUNCTION: This class contains all miscellaneous
				 data and functions for this simulation.
 -------------------------------------------------- */

#include "stdio.h"
#include "stdlib.h"
#include "string.h"
#include "math.h"

#ifndef _SIM_PARAMS_CPP
#define _SIM_PARAMS_CPP

#include "simParams.h"

extern int		RANDOM_SEED;
extern char		DATA_DIRECTORY[100];
extern int		DATA_FILE_BUFFER;
extern int		NUM_MUTATIONS;
extern int		NUM_HIDDEN_NEURONS;

extern char		TEMP_FILENAME_PREFIX[100];
extern char		TEMP_FILENAME[100];
extern char		TAUS_OUT_FILENAME[100];
extern char		WEIGHTS_OUT_FILENAME[100];
extern char		OMEGAS_OUT_FILENAME[100];
extern char		SENSORS_OUT_FILENAME[100];
extern char		BODY_OUT_FILENAME[100];
extern char		SENSOR_IN_FILENAME[100];

SIM_PARAMS::SIM_PARAMS(int argc, char **argv) {

	startTime = time(NULL);

	randSeed = RANDOM_SEED;
	numMutations = NUM_MUTATIONS;
	numHiddenNeurons = NUM_HIDDEN_NEURONS;

	ParseParameters(argc,argv);

	sprintf(tempFileName,	"%s%d/%s",TEMP_FILENAME_PREFIX,randSeed,TEMP_FILENAME);
	sprintf(tausFileName,	"%s%d/%s",TEMP_FILENAME_PREFIX,randSeed,TAUS_OUT_FILENAME);
	sprintf(weightsFileName,"%s%d/%s",TEMP_FILENAME_PREFIX,randSeed,WEIGHTS_OUT_FILENAME);
	sprintf(omegasFileName,	"%s%d/%s",TEMP_FILENAME_PREFIX,randSeed,OMEGAS_OUT_FILENAME);
	sprintf(sensorsFileName,"%s%d/%s",TEMP_FILENAME_PREFIX,randSeed,SENSORS_OUT_FILENAME);
	sprintf(bodyFileName,	"%s%d/%s",TEMP_FILENAME_PREFIX,randSeed,BODY_OUT_FILENAME);
	sprintf(sensorFileName,	"%s%d/%s",TEMP_FILENAME_PREFIX,randSeed,SENSOR_IN_FILENAME);

	srand(randSeed);
}

SIM_PARAMS::~SIM_PARAMS(void) {

}

void  SIM_PARAMS::CloseDataFiles(void) {

}

void  SIM_PARAMS::DirectoryMake(char *dirName) {

	char command[500];

	sprintf(command,"rm -r %s",dirName);
	system(command);

	sprintf(command,"mkdir %s",dirName);
	system(command);
}

void  SIM_PARAMS::FileCreate(char *fileName) {

}

void  SIM_PARAMS::FileDelete(char *fileName) {

	char command[100];

	sprintf(command,"rm %s",fileName);

	system(command);
}

int   SIM_PARAMS::FileExists(char *fileName) {

	int exists;

	ifstream *inFile = new ifstream(fileName,ios::in);

	if ( inFile->good() )
		exists = true;

	else
		exists = false;

	inFile->close();
	delete inFile;
	inFile = NULL;

	return( exists );
}

void SIM_PARAMS::FileRename(char *src, char *dest) {

	char command[200];

	sprintf(command,"mv %s %s",src,dest);

	system(command);
}

int SIM_PARAMS::FlipCoin(void) {

	return( Rand(0.0,1.0) < 0.5 );
}

ofstream *SIM_PARAMS::GetOutFile(char *fileName) {

	ofstream *outFile = new ofstream(fileName);

	return( outFile );
}

double SIM_PARAMS::HoursSinceStart(void) {

	double hoursSinceStart = double(time(NULL) - startTime) / 3600.0;

	return( hoursSinceStart );
}

void  SIM_PARAMS::ParseParameters(int argc, char **argv) {

	int currParam;

	for(currParam=0;currParam<argc;currParam++) {

		if ( strcmp(argv[currParam],"-r") == 0 )
			randSeed = atoi(argv[currParam+1]);

		if ( strcmp(argv[currParam],"-m") == 0 )
			numMutations = atoi(argv[currParam+1]);

		if ( strcmp(argv[currParam],"-h") == 0 )
			numHiddenNeurons = atoi(argv[currParam+1]);
	}
}

double SIM_PARAMS::Rand(double min, double max) {

	double zeroToOne = ((double)rand()) / RAND_MAX;
	double returnVal;

	returnVal = (zeroToOne * (max-min)) + min;
	return returnVal;
}

double SIM_PARAMS::RandGaussian(void) {

	double w = 1.01;
	double x1, x2;

	while ( w >= 1.0 ) {
		x1 = 2.0*Rand(0,1) - 1;
		x2 = 2.0*Rand(0,1) - 1;
		w = x1*x1 + x2*x2;
	}	
	w = sqrt( (-2.0*log(w))/w );
	
	return( x1*w );
}

int SIM_PARAMS::RandInt(int min, int max) {

	if ( min == max )
		return( min );
	else
		return( (rand() % (max-min+1)) + min );
}

double SIM_PARAMS::Scale(double value, double min1, double max1,
								 double min2, double max2) {

	if ( min1 < 0 )
		value = value - min1;
	else
		value = value + min1;

	return( (value*(max2-min2)/(max1-min1)) + min2 );
}

void SIM_PARAMS::WaitForFile(char *fileName) {

	while ( !FileExists(fileName) );
}

#endif
