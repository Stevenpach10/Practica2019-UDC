/* ---------------------------------------------------
   FILE:     genome.cpp
	AUTHOR:   Josh Bongard
	DATE:     October 2, 2000
	FUNCTION: This class contains all information for
				 a single physical segment of an organism
				 in the MathEngine environment.
 -------------------------------------------------- */
#include "math.h"

#ifndef _GENOME_CPP
#define _GENOME_CPP
#include "genome.h"
#include "matrix.h"
#include "simParams.h"

extern SIM_PARAMS *simParams;
extern char SENSOR_IN_FILENAME[100];
extern double TAR_OBJ_MAX_DIST;

extern double TAU_MIN;
extern double TAU_MAX;
extern double WEIGHT_MIN;
extern double WEIGHT_MAX;
extern double OMEGA_MIN;
extern double OMEGA_MAX;
extern double SENSOR_MIN;
extern double SENSOR_MAX;

extern int    NUM_GENERATIONS;
extern double SUCCESS_CLAW_ROTATION;
extern double CLAW_ROTATION_MAX;

extern int EVAL_PERIOD;

extern int NUM_TOUCH_SENSORS;
extern int NUM_ANGLE_SENSORS;

extern int HEADER_LENGTH;
extern int WINDOW_LENGTH;

extern int NUM_SENSORS;
extern int NUM_HIDDEN;
extern int NUM_MOTORS;

extern double Z_OFFSET;
extern double DANGLER_LENGTH;

extern double MAX_MASS_PER_PART;
extern double MUTATION_BIAS;

extern int NUM_NEURONS;

extern double SUCCESSFUL_TARGET_OBJECT_PROXIMITY;

extern int DATA_COL_EVAL_TIME;

GENOME::GENOME() {

	mutInTaus		= 0;
	mutInWeights		= 0;
	mutInOmegas		= 0;
	mutInSensorWeights	= 0;

	totalNeurons = NUM_NEURONS+simParams->numHiddenNeurons;

	taus = new MATRIX(1,totalNeurons);
	for (int i=0;i<totalNeurons;i++)
		taus->Set(0,i,simParams->Rand(TAU_MIN,TAU_MAX));

	weights = new MATRIX(totalNeurons,totalNeurons);
	for (int i=0;i<totalNeurons;i++)
		for (int j=0;j<totalNeurons;j++)
			weights->Set(i,j,simParams->Rand(WEIGHT_MIN,WEIGHT_MAX));

	omegas = new MATRIX(1,totalNeurons);
	for (int i=0;i<totalNeurons;i++)
		omegas->Set(0,i,simParams->Rand(OMEGA_MIN,OMEGA_MAX));

	sensorWeights = new MATRIX(NUM_SENSORS,totalNeurons);
	for (int i=0;i<NUM_SENSORS;i++)
		for (int j=0;j<totalNeurons;j++)
			sensorWeights->Set(i,j,simParams->Rand(SENSOR_MIN,SENSOR_MAX));
}

GENOME::GENOME(GENOME *parent) {

	mutInTaus		= 0;
	mutInWeights		= 0;
	mutInOmegas		= 0;
	mutInSensorWeights	= 0;

	totalNeurons = parent->totalNeurons;

	taus = new MATRIX(parent->taus);

	weights = new MATRIX(parent->weights);

	omegas = new MATRIX(parent->omegas);

	sensorWeights = new MATRIX(parent->sensorWeights);
}

GENOME::~GENOME(void) {

	delete taus;
	taus = NULL;

	delete weights;
	weights = NULL;

	delete omegas;
	omegas = NULL;

	delete sensorWeights;
	sensorWeights = NULL;
}

int GENOME::CalculateFitness(	int currentGeneration, int evaluationLength, double distOfTarget,
				MATRIX *dataForOutputFile, int rowIndex) {

	ifstream *inFile = new ifstream(simParams->sensorFileName,ios::in);

	double tmp;
	(*inFile) >> tmp;

	MATRIX *sensorVals = new MATRIX(inFile);

	inFile->close();
	delete inFile;
	inFile = NULL;

	simParams->FileDelete(simParams->sensorFileName);

	double distSNU;
	double touchCTL;
	double distCTL;
	double touchCTR;
	double distCTR;
	double angleCB;
	fitness = 0.0;
	for (int i=0;i<sensorVals->length-1;i++) {

		distSNU  = sensorVals->Get(i,0);
		touchCTL = sensorVals->Get(i,1);
		distCTL  = sensorVals->Get(i,2);
		touchCTR = sensorVals->Get(i,3);
		distCTR  = sensorVals->Get(i,4);
		angleCB  = sensorVals->Get(i,5);

		if ( touchCTL && touchCTR ) {
			if ( (1+distSNU) > fitness )	
				fitness = 1 + distSNU;
		}
		else {
			if ( distCTL*distCTR > fitness )
				fitness = distCTL*distCTR;
		}
	}

	int allZeros = true;
	for (int j=0;j<NUM_SENSORS;j++)
		allZeros = allZeros && (sensorVals->Get(sensorVals->length-1,j)==0);

	if ( allZeros )
		fitness = 0.0;

	dataForOutputFile->Set(rowIndex,2,fitness);
	dataForOutputFile->Set(rowIndex,3,evaluationLength);
	dataForOutputFile->Set(rowIndex,4,distOfTarget);
	dataForOutputFile->Set(rowIndex,5,distSNU);
	dataForOutputFile->Set(rowIndex,6,touchCTL);
	dataForOutputFile->Set(rowIndex,7,distCTL);
	dataForOutputFile->Set(rowIndex,8,touchCTR);
	dataForOutputFile->Set(rowIndex,9,distCTR);
	dataForOutputFile->Set(rowIndex,10,angleCB);
	dataForOutputFile->Set(rowIndex,11,mutInTaus);
	dataForOutputFile->Set(rowIndex,12,mutInWeights);
	dataForOutputFile->Set(rowIndex,13,mutInOmegas);
	dataForOutputFile->Set(rowIndex,14,mutInSensorWeights);
	dataForOutputFile->Set(rowIndex,15,simParams->HoursSinceStart());

	dataForOutputFile->Set(rowIndex,DATA_COL_EVAL_TIME,sensorVals->length);

	printf("[g: %d of %d] ",currentGeneration,NUM_GENERATIONS);
	printf("[f: %5.5f] ",fitness);
	printf("[e: %d %d] ",evaluationLength,sensorVals->length);
	printf("[d: %3.3f] ",distOfTarget);
	printf("[s: ");
		printf("%3.3f "	,distSNU);
		printf("%d "	,int(touchCTL));
		printf("%3.3f "	,distCTL);
		printf("%d "	,int(touchCTR));
		printf("%3.3f "	,distCTR);
		printf("%3.3f"	,angleCB);
	printf("] ");

	printf("[t: %3.3f] ",simParams->HoursSinceStart());

	printf("[m: %d %d %d %d]\n",
		mutInTaus,mutInWeights,mutInOmegas,mutInSensorWeights);

	int success = Success(sensorVals);

	delete sensorVals;
	sensorVals = NULL;

	return( success );
}

void GENOME::LesionSensor(int sensorIndex) {

	for (int j=0;j<totalNeurons;j++)
		sensorWeights->Set(sensorIndex,j,0.0);
}

void GENOME::Mutate(void) {

	int numVals = 	totalNeurons + 
			totalNeurons*totalNeurons + 
			totalNeurons + 
			NUM_SENSORS*totalNeurons;

	double mutProb = double(simParams->numMutations) / double(numVals);
	int mutationMade = false;

	while ( !mutationMade ) {

		for (int j=0;j<totalNeurons;j++)
			if ( simParams->Rand(0,1) < mutProb ) {
				taus->Set(0,j,simParams->Rand(TAU_MIN,TAU_MAX));
				mutationMade = true;
				mutInTaus++;
			}

		for (int i=0;i<totalNeurons;i++)
			for (int j=0;j<totalNeurons;j++)
				if ( simParams->Rand(0,1) < mutProb ) {
					weights->Set(i,j,simParams->Rand(WEIGHT_MIN,WEIGHT_MAX));
					mutationMade = true;
					mutInWeights++;
				}

		for (int j=0;j<totalNeurons;j++)
			if ( simParams->Rand(0,1) < mutProb ) {
				omegas->Set(0,j,simParams->Rand(OMEGA_MIN,OMEGA_MAX));
				mutationMade = true;
				mutInOmegas++;
			}

		for (int i=0;i<NUM_SENSORS;i++)
			for (int j=0;j<totalNeurons;j++)
				if ( simParams->Rand(0,1) < mutProb ) {
					sensorWeights->Set(i,j,simParams->Rand(SENSOR_MIN,SENSOR_MAX));
					mutationMade = true;
					mutInSensorWeights++;
				}
	}
}

void GENOME::SendAsBrain(int fileIndex) {

	char fileName[300];
	
	ofstream *outFile = new ofstream(simParams->tempFileName);
	(*outFile) << "1\n";
	taus->Write(outFile);
	outFile->close();
	delete outFile;
	if ( fileIndex==-1 )
		simParams->FileRename(	simParams->tempFileName,
					simParams->tausFileName);
	else {
		sprintf(fileName,"../Data/%d_Taus_%d.dat",simParams->randSeed,fileIndex);
		simParams->FileRename(simParams->tempFileName,fileName);
	}

	outFile = new ofstream(simParams->tempFileName);
	(*outFile) << "1\n";
	weights->Write(outFile);
	outFile->close();
	delete outFile;
	if ( fileIndex==-1 )
		simParams->FileRename(simParams->tempFileName,
					simParams->weightsFileName);
	else {
		sprintf(fileName,"../Data/%d_Weights_%d.dat",simParams->randSeed,fileIndex);
		simParams->FileRename(simParams->tempFileName,fileName);
	}

	outFile = new ofstream(simParams->tempFileName);
	(*outFile) << "1\n";
	omegas->Write(outFile);
	outFile->close();
	delete outFile;
	if ( fileIndex==-1 )
		simParams->FileRename(simParams->tempFileName,
					simParams->omegasFileName);
	else {
		sprintf(fileName,"../Data/%d_Omegas_%d.dat",simParams->randSeed,fileIndex);
		simParams->FileRename(simParams->tempFileName,fileName);
	}

	outFile = new ofstream(simParams->tempFileName);
	(*outFile) << "1\n";
	sensorWeights->Write(outFile);
	outFile->close();
	delete outFile;
	if ( fileIndex==-1 )
		simParams->FileRename(simParams->tempFileName,
					simParams->sensorsFileName);
	else {
		sprintf(fileName,"../Data/%d_Sensors_%d.dat",simParams->randSeed,fileIndex);
		simParams->FileRename(simParams->tempFileName,fileName);
	}
}

// ------------------------ Private methods ------------------------------

int  GENOME::Success(MATRIX *sensorVals) {

	int success = false;

	int i=0;

	while ( (i<sensorVals->length) && (!success) ) {

		double distSNU  = sensorVals->Get(i,0);
		double touchCTL = sensorVals->Get(i,1);
		double distCTL  = sensorVals->Get(i,2);
		double touchCTR = sensorVals->Get(i,3);
		double distCTR  = sensorVals->Get(i,4);
		double angleCB  = sensorVals->Get(i,5);

		if ( (distSNU > 0.825) && touchCTL && touchCTR )
			success = true;
		else
			i++;
	}

	return( success );
}

#endif
