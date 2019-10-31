/* ---------------------------------------------------
   FILE:     constants.h
	AUTHOR:   Josh Bongard
	DATE:     March 21, 2001
	FUNCTION: This class contains all of the constants
			    for this project.
 -------------------------------------------------- */

#ifndef _CONSTANTS_H
#define _CONSTANTS_H

int			RANDOM_SEED			= 0;

int			NUM_GENERATIONS			= 100000;

int			NUM_MUTATIONS			= 1;
int			NUM_HIDDEN_NEURONS		= 0;

double			SUCCESSFUL_TARGET_OBJECT_PROXIMITY = 0.67;

// ----------------------------------------------------------------
//                   Behavior chaining constants
// ----------------------------------------------------------------

int			NUM_SENSORS			= 2 + 3 + 1;
// Two touch sensors; three distance sensors; one angle sensor

int			NUM_NEURONS			= 1+2+8;
// one motor neuron (clawbase-mainbody)
// two claw motor neurons
// eight leg motor neurons

int			DATA_FILE_BUFFER_WIDTH		= 11 + NUM_SENSORS + NUM_SENSORS + 1;

int			DATA_COL_ROBUSTNESS		= 11 + NUM_SENSORS - 1;
int			DATA_COL_LESIONS		= DATA_COL_ROBUSTNESS+1;
int			DATA_COL_EVAL_TIME		= DATA_COL_LESIONS + NUM_SENSORS;

char			TEMP_FILENAME_PREFIX[100]	= "/tmp/Files";
char			TEMP_FILENAME[100] 		= "temp.dat";
char			TAUS_OUT_FILENAME[100]   	= "Taus.dat";
char			WEIGHTS_OUT_FILENAME[100]   	= "Weights.dat";
char			OMEGAS_OUT_FILENAME[100]   	= "Omegas.dat";
char			SENSORS_OUT_FILENAME[100]	= "SensorWeights.dat";

char			BODY_OUT_FILENAME[100] 		= "Body.dat";
char			SENSOR_IN_FILENAME[100] 	= "Sensors.dat";

double			TAU_MIN				= 0.1;
double			TAU_MAX				= 0.5;
double			WEIGHT_MIN			= -16;
double			WEIGHT_MAX			= 16;
double			OMEGA_MIN			= -4;
double			OMEGA_MAX			= 4;
double			SENSOR_MIN			= WEIGHT_MIN;
double			SENSOR_MAX			= WEIGHT_MAX;


double			DIST_SENSOR_MAX_RANGE		= 5.0;

double			TAR_OBJ_WIDTH			= 0.4;
double			TAR_OBJ_HEIGHT			= 1.4;

double			TAR_OBJ_MAX_DIST		= 10.0;

double			BODY_WIDTH			= 1.0;
double			BODY_LENGTH			= 3.0;
double			BODY_DEPTH			= 0.3;

double			CLAW_ARM_RADIUS			= 0.1;
double			CLAW_ARM_LENGTH			= 1.5*TAR_OBJ_WIDTH;

double			LEG_RADIUS			= 0.1;
double			NUB_RADIUS			= 0.15;

double			LEG_EXTENSION_MAX		= 20.0;
double			CLAWBASE_ROTATION_MAX		= 120.0;
double			CLAW_ROTATION_MAX		= 45.0;
double			CLAWTIP_ROTATION_MAX		= 120 - CLAW_ROTATION_MAX;

double			MOTOR_LEG_MAX_FORCE		= 200;
double			MOTOR_CLAW_BASE_MAX_FORCE	= 200;
double			MOTOR_CLAW_MAX_FORCE		= 50;

double			MOTOR_SPEED			= 5;

double			SUCCESS_CLAW_ROTATION		= 45.0;

int			EVALUATION_LENGTH		= 100;
double			START_TARGET_DISTANCE		= 0.0;

double			HARDEN_ENVIRONMENT_INCREMENT	= 0.01;
int			LENGTHEN_TIME_INCREMENT		= 10;

int			MAX_EVALS_BEFORE_FAILURE	= 100;

int			DATA_FILE_BUFFER		= 100;

#endif
