// ---------------------------------------------------
//    FILE:     nnetwork.cpp
//		AUTHOR:	 Josh Bongard
//		DATE:     March 26, 2001
//		FUNCTION: This class defines a neural network to
//              control a user-designed agent.
// --------------------------------------------------- 
#include "stdio.h"

#include "nnetwork.h"
#include "simParams.h"

#include <ode/ode.h>
#include <drawstuff/drawstuff.h>

extern int  TOUCH_SENSORS;
extern int  PROP_SENSORS;

extern int  BIAS_NODES;

extern SIM_PARAMS  *simParams;
extern double STEP_SIZE;

NEURAL_NETWORK::NEURAL_NETWORK(	ifstream *tauFile, ifstream *weightFile,
				ifstream *omegaFile, ifstream *sensorWFile) {

	taus = new MATRIX(tauFile);
	weights = new MATRIX(weightFile);
	omegas = new MATRIX(omegaFile);
	sensorWeights = new MATRIX(sensorWFile);

	sensors = NULL;

	numInput = 0;
	numOutput = 0;
	numNeurons = omegas->width;

	neurons = new MATRIX(1,numNeurons,0.0);
	for (int i=0;i<numNeurons;i++)
		neurons->Set(0,i,0);

	currY = new MATRIX(numNeurons,1,0);
	kn1 = new MATRIX(numNeurons,1,0);
	kn2 = new MATRIX(numNeurons,1,0);
	kn3 = new MATRIX(numNeurons,1,0);
	kn4 = new MATRIX(numNeurons,1,0);
}

NEURAL_NETWORK::~NEURAL_NETWORK(void) {
	
	delete taus;
	taus = NULL;

	delete weights;
	weights = NULL;

	delete omegas;
	omegas = NULL;

	delete sensorWeights;
	sensorWeights = NULL;

	delete sensors;
	sensors = NULL;

	delete neurons;
	neurons = NULL;

	delete currY;
	currY = NULL;

	delete kn1;
	kn1 = NULL;
	
	delete kn2;
	kn2 = NULL;

	delete kn3;
	kn3 = NULL;

	delete kn4;
	kn4 = NULL;
}

int NEURAL_NETWORK::AddMotor(void) {

	numOutput++;

	return(numOutput-1);
}

int NEURAL_NETWORK::AddSensor(void) {

	numInput++;

	return(numInput-1);
}

void NEURAL_NETWORK::CreateSensors(void) {

	sensors = new MATRIX(1,numInput,0.0);
}

double NEURAL_NETWORK::GetNeuronOutput(int neuronIndex) {

	return( 1/(1+exp(omegas->Get(0,neuronIndex) - neurons->Get(0,neuronIndex))) );
}

void NEURAL_NETWORK::ResetSensors(void) {

	for (int i=0;i<numInput;i++)
		sensors->Set(0,i,0);
}

void NEURAL_NETWORK::SetTouchSensor(int neuronID) {

	sensors->Set(0,neuronID,1.0);
}

void NEURAL_NETWORK::Update(void){

	int i;

	for (i=0;i<numNeurons;i++)
		currY->vals[i] = neurons->vals[i];
	UpdateNeurons(kn1,currY);

	for (i=0;i<numNeurons;i++)
		currY->vals[i] = neurons->vals[i] + (STEP_SIZE*kn1->vals[i]/2.0 );
	UpdateNeurons(kn2,currY);

	for (i=0;i<numNeurons;i++)
		currY->vals[i] = neurons->vals[i] + (STEP_SIZE*kn2->vals[i]/2.0 );
	UpdateNeurons(kn3,currY);

	for (i=0;i<numNeurons;i++)
		currY->vals[i] = neurons->vals[i] + (STEP_SIZE*kn3->vals[i] );

	UpdateNeurons(kn4,currY);

	for (i=0;i<numNeurons;i++)
		neurons->vals[i] = neurons->vals[i] +
					(STEP_SIZE/6.0)*(
					kn1->vals[i] +
					2*kn2->vals[i] +
					2*kn3->vals[i] +
					kn4->vals[i]
					);
}

// --------------------- Private methods --------------------------
void NEURAL_NETWORK::UpdateNeurons(MATRIX *kn, MATRIX *currY) {

	for (int i=0;i<numNeurons;i++) {

		kn->vals[i] = -currY->vals[i];

		for (int j=0;j<numNeurons;j++)
			kn->vals[i] = kn->vals[i] + 
					weights->vals[i*weights->width+j] *
					1/( 1 + exp( omegas->vals[j] - currY->vals[j] ) );

		for (int j=0;j<numInput;j++)
			kn->vals[i] = kn->vals[i] + 
					sensorWeights->vals[j*sensorWeights->width+i]*
					sensors->vals[j];

		kn->vals[i] = kn->vals[i] / taus->vals[i];
	}
}
