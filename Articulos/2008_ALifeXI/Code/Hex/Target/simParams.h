/* ---------------------------------------------------
   FILE:     simParams.h
	AUTHOR:   Josh Bongard
	DATE:     October 5, 2000
	FUNCTION: This class contains all miscellaneous
				 data and functions for this simulation.
 -------------------------------------------------- */
#include "fstream"
#include "matrix.h"

#ifndef _SIM_PARAMS_H
#define _SIM_PARAMS_H

class SIM_PARAMS {

public:
	int			rendererCreated;
	ifstream		inBestAgentFile;
	int			internalTimer;
	int			evalOver;
	int			runNumber;
	int			functionAsReader;
	int			fitnessReported;
	char		genomeFileName[40];
	char		envFileName[40];
	int			randSeed;
	int			showNetwork;
	ofstream	*footprintFile;
	ofstream	*torqueFile;
	ofstream	*hiddenLayerFile;
	ofstream	*plumeFile;
	ofstream	*noiseFile;
	ofstream	*debrisFile;
	ofstream	*trajectoryFile;
	double		displacementDistance;
	int			rendering;
	int			debrisType;
	int			noiseIteration;
	int			useTransparency;
	int			drawNetwork;
	int			evalPeriod;
	int			evaluating;
	ifstream	*bodyFile;
	ifstream	*tauFile;
	ifstream	*weightFile;
	ifstream	*omegaFile;
	ifstream	*sensorWFile;
	ofstream	*sensorFile;
	int		agentsToEvaluate;
	int		numTests;
	MATRIX		**motorCommands;
	int		numSensors;
	int		currentTest;
	MATRIX		*connectedObjects;
	int		agentExploding;
	int		testForExplosions;
	int		recordMovie;
	int		currFrame;
	int		indexToPlayback;
	int		forwardPlayback;
	char 		tempFileName[200];
	char 		tausFileName[200];
	char 		weightsFileName[200];
	char 		omegasFileName[200];
	char 		sensorsFileName[200];
	char 		bodyFileName[200];
	char 		sensorFileName[200];

public:
	SIM_PARAMS(int argc, char **argv);
	~SIM_PARAMS(void);
	double  AngleBetween(double *v1, double *v2);
	void	CloseFiles(void);
	void	CloseOutputFiles(void);
	void	Cross(double *v1, double *v2, double *v3);
	void	DestroyMotorCommands(void);
	double	DistBetween(double  *v1, double *v2);
	double	Dot(double *v1, double *v2);
	void	FileCopy(char *src, char *dest);
	void    FileDelete(char *fileName);
	int     FileExists(char *fileName);
	void    FileRename(char *src, char *dest);
	int	FlipCoin(void);
	void    GetMotorCommands(void);
	double	MagnitudeOfVector(double *vect);
	void	Normalize(double *v);
	void	OpenFiles(void);
	double	Rand(double min, double max);
	int		RandInt(int min, int max);
	double	Scale(double value, double min1, double max1,
					double min2, double max2);
	void	SetDefaultRotation(float *R);
	void	VectAdd(double *v1, double *v2, double *v3);
	void	VectMult(double *v, double amt);
	void	VectSub(double *v1, double *v2, double *v3);
	void	WriteToNoiseFile(double fit);

private:
	void	ParseParameters(int argc, char **argv);
	void	PrintHelp(void);
};

#endif
