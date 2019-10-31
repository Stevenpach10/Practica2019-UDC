/* ---------------------------------------------------
   FILE:     growGA.h
	AUTHOR:   Josh Bongard
	DATE:     October 20, 2000
	FUNCTION: This class contains all information for
			  a population of variable-length genotypes

 -------------------------------------------------- */

#ifndef _GA_H
#define _GA_H

#include "iostream"
#include "fstream"
#include "genome.h"

class GA {

public:
	GENOME	*parentGenome;
	GENOME  *childGenome;
	int	evaluationLength;
	double	distOfTarget;
	int	numSuccesses;
	int	evalsSinceLastSuccessOrFailure;

	int      popSize;
	int      currGeneration;
	int      totalGenerations;
	GENOME   **genomes;
	GENOME	 **parents;
	GENOME	 **children;
	char	 dataFileName[200];
	MATRIX	 *dataForOutputFile;
	int	 rowIndex;

private:
	double    *bestFits;
	double    *avgFits;
	int		   nextAvailableID;
	ofstream  *fitFile;
	ofstream  *genomeFile;
	char	  fitFileName[100];
	char	  genomeFileName[100];
	int		  stagnationCounter;

public:
	GA(void);
	~GA(void);
	void	Evolve();
	void	SendBody(int fileIndex);

private:
	void	CheckLesions(int currGen);
	void    CheckRobustness(int currGen);
	int     EaseTask(int currGen);
	int 	Failure(void);
	int     HardenTask(int currGen);
	void    LengthenTime(void);
	void	MakeChallengeHarder(void);
	void    SaveOutData(void);
	void    SendClaws(ofstream *outFile);
	void	SendClawTips(ofstream *outFile);
	void	SendJointsClaw(ofstream *outFile);
	void	SendJointsClawTips(ofstream *outFile);
	void	SendJointsLegs(ofstream *outFile);
	void	SendJointsFrontLegs(ofstream *outFile);
	void	SendJointsBackLegs(ofstream *outFile);
	void	SendJointsSensorNubs(ofstream *outFile);
	void	SendLegs(ofstream *outFile);
	void    SendMainBody(ofstream *outFile);
	void    SendPostscript(ofstream *outFile);
	void	SendSensorNubs(ofstream *outFile);
	void    SendTargetObject(ofstream *outFile);
	void	SendUpperLegs(ofstream *outFile);
	void	WaitForSensorReadings(void);
};

#endif
