/* ---------------------------------------------------
   FILE:      nnetwork.h
	AUTHOR:   Chandana Paul
	DATE:     November 27, 2000
	FUNCTION: This class contains the neural network
			  which controls the biped agent. 	
 -------------------------------------------------- */
#include "fstream"
#include "math.h"
#include "matrix.h"

#ifndef _NEURAL_NETWORK_H
#define _NEURAL_NETWORK_H

class NEURAL_NETWORK {

public:

	MATRIX *taus;
	MATRIX *weights;
	MATRIX *omegas;
	MATRIX *sensorWeights;

	MATRIX *sensors;

	int   numInput;
	int   numOutput;
	int   numNeurons;	
	MATRIX *neurons;

	MATRIX *currY;
	MATRIX *kn1;
	MATRIX *kn2;
	MATRIX *kn3;
	MATRIX *kn4;

	int   numHidden;

private:
	MATRIX *inputValues;
	MATRIX *hiddenValues;
	MATRIX *outputValues;

	MATRIX *nextHiddenValues;
	MATRIX *nextOutputValues;

	MATRIX *ih;
	MATRIX *hh;
	MATRIX *ho;

public:
	NEURAL_NETWORK(ifstream *tauFile, ifstream *weightFile, ifstream *omegaFile, ifstream *sensorWFile);
	~NEURAL_NETWORK(void);
	int   AddMotor(void);
	int   AddSensor(void);
	void  CreateSensors(void);
	double GetNeuronOutput(int neuronIndex);
	void  Print(void);
	void  ResetSensors(void);
	void  SetTouchSensor(int neuronIndex);
	void  Update(void);
private:
	void UpdateNeurons(MATRIX *kn, MATRIX *currY);
};

#endif
