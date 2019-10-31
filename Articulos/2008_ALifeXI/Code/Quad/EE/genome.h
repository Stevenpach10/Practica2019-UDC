/* ---------------------------------------------------
   FILE:     bodyPlan.h
	AUTHOR:   Josh Bongard
	DATE:     October 2, 2000
	FUNCTION: This class contains all information for
				 a single physical segment of an organism
				 in the MathEngine environment.
 -------------------------------------------------- */

#ifndef _GENOME_H
#define _GENOME_H

#include "matrix.h"

class GENOME {

public:
	MATRIX *taus;
	MATRIX *weights;
	MATRIX *omegas;
	MATRIX *sensorWeights;

	int	mutInTaus;
	int	mutInWeights;
	int	mutInOmegas;
	int	mutInSensorWeights;

	int	totalNeurons;

	double fitness;

public:
	GENOME();
	GENOME(GENOME *parent);
	~GENOME(void);
	int  CalculateFitness(	int currentGeneration, int evaluationLength, double distOfTarget,
				MATRIX *dataForOutputFile, int rowIndex);
	void LesionSensor(int sensorIndex);
	void Mutate(void);
	void SaveSensorData(void);
	void SendAsBrain(int fileIndex);

private:
	int Success(MATRIX *sensorVals);
};

#endif
