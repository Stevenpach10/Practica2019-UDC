/* ---------------------------------------------------
   FILE:     growGA.cpp
	AUTHOR:   Josh Bongard
	DATE:     October 20, 2000
	FUNCTION: This class contains all information for
				 a population of variable-length genotypes
 -------------------------------------------------- */
#include "stdio.h"
#include "stdlib.h"
#include "math.h"

#ifndef _GA_CPP
#define _GA_CPP

#include "constants.h"
#include "genome.h"
#include "ga.h"
#include "simParams.h"

extern SIM_PARAMS	*simParams;
extern char			TEMP_FILENAME[100];
extern double			TAR_OBJ_WIDTH;
extern double			TAR_OBJ_HEIGHT;

extern double			BODY_WIDTH;
extern double			BODY_LENGTH;
extern double			BODY_DEPTH;

extern double			CLAW_ARM_RADIUS;
extern double			CLAW_ARM_LENGTH;

extern int			EVALUATION_LENGTH;
extern double			START_TARGET_DISTANCE;

extern double			HARDEN_ENVIRONMENTAL_INCREMENT;
extern int			LENGTHEN_TIME_INCREMENT;
extern int			MAX_EVALS_BEFORE_FAILURE;

GA::GA(void) {

	char dirName[200];
	sprintf(dirName,"%s%d",TEMP_FILENAME_PREFIX,simParams->randSeed);
	simParams->DirectoryMake(dirName);

	sprintf(dataFileName,"../Data/runData_%d.dat",simParams->randSeed);
	simParams->FileDelete(dataFileName);

	ofstream *outFile = new ofstream(dataFileName);
	outFile->close();
	delete outFile;

	dataForOutputFile = new MATRIX(DATA_FILE_BUFFER,DATA_FILE_BUFFER_WIDTH,0.0);
	rowIndex = 0;

	parentGenome = new GENOME;
	childGenome = NULL;

	evaluationLength = EVALUATION_LENGTH;
	evalsSinceLastSuccessOrFailure = 0;
	distOfTarget = START_TARGET_DISTANCE;
	numSuccesses = 0;
}
GA::~GA(void) {

	if ( parentGenome ) {
		delete parentGenome;
		parentGenome = NULL;
	}
	if ( childGenome ) {
		delete childGenome;
		childGenome = NULL;
	}
}

void GA::Evolve(void) {

	int success;

	parentGenome->SendAsBrain(-1);
	SendBody(-1);
	WaitForSensorReadings();
	dataForOutputFile->Set(rowIndex,0,0);
	dataForOutputFile->Set(rowIndex,1,parentGenome->fitness);
	success = parentGenome->CalculateFitness(0,evaluationLength,distOfTarget,dataForOutputFile,rowIndex);
	SaveOutData();

	for (int i=1;i<NUM_GENERATIONS;i++) {

		//childGenome = new GENOME;
		childGenome = new GENOME(parentGenome);
		childGenome->Mutate();

		childGenome->SendAsBrain(-1);
		SendBody(-1);
		WaitForSensorReadings();
		printf("[p: %5.5f] ",parentGenome->fitness);
		dataForOutputFile->Set(rowIndex,0,i);
		dataForOutputFile->Set(rowIndex,1,parentGenome->fitness);
		success = childGenome->CalculateFitness(i,evaluationLength,distOfTarget,
							dataForOutputFile,rowIndex);

		if ( (childGenome->fitness >= parentGenome->fitness) || success ) {
			printf("*****\n");
			delete parentGenome;
			parentGenome = childGenome;
		}
		else
			delete childGenome;

		childGenome = NULL;

		evalsSinceLastSuccessOrFailure++;

		if ( Failure() )
			success = EaseTask(i);

		while ( success )
			success = HardenTask(i);

		SaveOutData();
	}
}

void GA::SendBody(int fileIndex) {

	ofstream *outFile = new ofstream(simParams->tempFileName);

	(*outFile) << "1\n";
	(*outFile) << "16 14\n";

	SendTargetObject(outFile);

	SendMainBody(outFile);
	SendSensorNubs(outFile);
	SendClaws(outFile);

	SendUpperLegs(outFile);
	SendLegs(outFile);

	SendJointsSensorNubs(outFile);

	SendJointsClaw(outFile);
	SendJointsClawTips(outFile);
	SendJointsLegs(outFile);

	SendPostscript(outFile);

	outFile->close();
	delete outFile;
	outFile = NULL;

	if ( fileIndex==-1 )
		simParams->FileRename(simParams->tempFileName,simParams->bodyFileName);
	else {
		char fileName[200];
		sprintf(fileName,"../Data/%d_Body_%d.dat",simParams->randSeed,fileIndex);
		simParams->FileRename(simParams->tempFileName,fileName);
	}
}

// ----------------------------------------------------------------
//                           Private methods
// ----------------------------------------------------------------

void GA::CheckLesions(int currGen) {

	GENOME *tempGenome;

	for (int i=0;i<NUM_SENSORS;i++) {
		tempGenome = new GENOME(parentGenome);
		tempGenome->LesionSensor(i);
		tempGenome->SendAsBrain(-1);
		SendBody(-1);
		WaitForSensorReadings();
		int success = tempGenome->CalculateFitness(currGen,evaluationLength,distOfTarget,
			dataForOutputFile,rowIndex);

		dataForOutputFile->Set(rowIndex,DATA_COL_LESIONS+i,tempGenome->fitness);

		delete tempGenome;
		tempGenome = NULL;
	}
}

void GA::CheckRobustness(int currGen) {

	GENOME *tempGenome = new GENOME(parentGenome);

	distOfTarget = distOfTarget/2.0;
	tempGenome->SendAsBrain(-1);
	SendBody(-1);
	WaitForSensorReadings();
	int sucess = tempGenome->CalculateFitness(currGen,evaluationLength,distOfTarget,
		dataForOutputFile,rowIndex);
	distOfTarget = distOfTarget*2.0;

	dataForOutputFile->Set(rowIndex,DATA_COL_ROBUSTNESS,tempGenome->fitness);

	delete tempGenome;
	tempGenome = NULL;
}

int GA::EaseTask(int currGen) {

	SaveOutData();

	LengthenTime();
	parentGenome->SendAsBrain(-1);
	SendBody(-1);
	WaitForSensorReadings();
	dataForOutputFile->Set(rowIndex,0,currGen);
	dataForOutputFile->Set(rowIndex,1,parentGenome->fitness);
	int success = parentGenome->CalculateFitness(currGen,evaluationLength,distOfTarget,
						dataForOutputFile,rowIndex);

	evalsSinceLastSuccessOrFailure = 0;

	return( success );
}

int GA::Failure(void) {

	return( evalsSinceLastSuccessOrFailure >= MAX_EVALS_BEFORE_FAILURE );
}

int GA::HardenTask(int currGen) {

	CheckRobustness(currGen);
	
	CheckLesions(currGen);

	parentGenome->SendAsBrain(-1);
	SendBody(-1);
	WaitForSensorReadings();
	int success = parentGenome->CalculateFitness(currGen,evaluationLength,distOfTarget,
		dataForOutputFile,rowIndex);

	SaveOutData();

	parentGenome->SendAsBrain(numSuccesses);
	SendBody(numSuccesses);
	numSuccesses++;

	MakeChallengeHarder();
	parentGenome->SendAsBrain(-1);
	SendBody(-1);
	WaitForSensorReadings();
	dataForOutputFile->Set(rowIndex,0,currGen);
	dataForOutputFile->Set(rowIndex,1,parentGenome->fitness);
	success = parentGenome->CalculateFitness(currGen,evaluationLength,distOfTarget,
						dataForOutputFile,rowIndex);

	evalsSinceLastSuccessOrFailure = 0;

	return( success );
}

void GA::LengthenTime(void) {

	evaluationLength = evaluationLength + LENGTHEN_TIME_INCREMENT;
}

void GA::MakeChallengeHarder(void) {

	distOfTarget     = distOfTarget + HARDEN_ENVIRONMENT_INCREMENT;
}

void GA::SaveOutData(void) {

	if ( rowIndex == (DATA_FILE_BUFFER-1) ) {
		dataForOutputFile->AppendToFile(dataFileName);
		dataForOutputFile->ReZero();
		rowIndex=0;
	}
	else
		rowIndex++;
}

void GA::SendClaws(ofstream *outFile) {

	(*outFile) << "\n( ClawBase \n";
	(*outFile) << "-position "	<< 0 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";

	(*outFile) << "-shape -sphere "	<<CLAW_ARM_RADIUS<<"\n";
	(*outFile) << "-mass 0.25 \n";
	(*outFile) << "-colour 0 0 0.5 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";

	(*outFile) << "\n( LeftClawArm \n";
	(*outFile) << "-position "	<< -CLAW_ARM_LENGTH/2.0 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-rotation 1 0 0 \n";
	(*outFile) << "-shape -cylinder "	<<CLAW_ARM_RADIUS*0.75<<" "
						<<CLAW_ARM_LENGTH<<"\n";
	(*outFile) << "-mass 0.25 \n";
	(*outFile) << "-colour 0 0 0.5 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";

	(*outFile) << "\n( RightClawArm \n";
	(*outFile) << "-position "	<< CLAW_ARM_LENGTH/2.0 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-rotation -1 0 0 \n";
	(*outFile) << "-shape -cylinder "	<<CLAW_ARM_RADIUS*0.75<<" "
						<<CLAW_ARM_LENGTH<<"\n";
	(*outFile) << "-mass 0.25 \n";
	(*outFile) << "-colour 0 0 0.5 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";

	SendClawTips(outFile);
}

void GA::SendClawTips(ofstream *outFile) {

	(*outFile) << "\n( LeftClawTip \n";
	(*outFile) << "-position "	<< -CLAW_ARM_LENGTH -CLAW_ARM_LENGTH/2 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-rotation -1 0 0 \n";
	(*outFile) << "-shape -cylinder "	<<CLAW_ARM_RADIUS<<" "
						<<CLAW_ARM_LENGTH<<"\n";
	(*outFile) << "-mass 0.25 \n";
	(*outFile) << "-colour 0 0 0.25 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << "-addTouchSensor \n";
	(*outFile) << "-addDistanceSensor TargetObject "<<DIST_SENSOR_MAX_RANGE<<"\n";
	(*outFile) << ") \n";

	(*outFile) << "\n( RightClawTip \n";
	(*outFile) << "-position "	<< CLAW_ARM_LENGTH + CLAW_ARM_LENGTH/2 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-rotation -1 0 0 \n";
	(*outFile) << "-shape -cylinder "	<<CLAW_ARM_RADIUS<<" "
						<<CLAW_ARM_LENGTH<<"\n";
	(*outFile) << "-mass 0.25 \n";
	(*outFile) << "-colour 0 0 0.25 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << "-addTouchSensor \n";
	(*outFile) << "-addDistanceSensor TargetObject "<<DIST_SENSOR_MAX_RANGE<<"\n";
	(*outFile) << ") \n";
}

void GA::SendJointsClaw(ofstream *outFile) {

	(*outFile) << "\n( ClawBase_MainBody\n";
	(*outFile) << "-connect ClawBase MainBody\n";
	(*outFile) << "-jointPosition "	<< 0 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<CLAWBASE_ROTATION_MAX<<" 1\n";
	(*outFile) << "-addSensor\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_CLAW_BASE_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";

	(*outFile) << "\n( LeftClawArm_ClawBase\n";
	(*outFile) << "-connect LeftClawArm ClawBase\n";
	(*outFile) << "-jointPosition "	<< 0 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 0 1 0\n";
	(*outFile) << "-jointLimits -"<<CLAW_ROTATION_MAX<<" 1\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_CLAW_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";

	(*outFile) << "\n( RightClawArm_ClawBase\n";
	(*outFile) << "-connect ClawBase RightClawArm\n";
	(*outFile) << "-jointPosition "	<< 0 << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 0 1 0\n";
	(*outFile) << "-jointLimits -"<<CLAW_ROTATION_MAX<<" 1\n";
	(*outFile) << "-shareMotor LeftClawArm_ClawBase\n";
	(*outFile) << "-motorForce "<<MOTOR_CLAW_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";
}

void GA::SendJointsClawTips(ofstream *outFile) {

	(*outFile) << "\n( LeftClawArm_LeftClawTip\n";
	(*outFile) << "-connect LeftClawArm LeftClawTip\n";
	(*outFile) << "-jointPosition "	<< -CLAW_ARM_LENGTH << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 0 1 0\n";
	(*outFile) << "-jointLimits -1 "<<CLAWTIP_ROTATION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_CLAW_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";

	(*outFile) << "\n( RightClawArm_RightClawTip\n";
	(*outFile) << "-connect RightClawTip RightClawArm\n";
	(*outFile) << "-jointPosition "	<< CLAW_ARM_LENGTH << " "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 0 1 0\n";
	(*outFile) << "-jointLimits -1 "<<CLAWTIP_ROTATION_MAX<<"\n";
	(*outFile) << "-shareMotor LeftClawArm_LeftClawTip\n";
	(*outFile) << "-motorForce "<<MOTOR_CLAW_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";
}

void GA::SendJointsLegs(ofstream *outFile) {

	SendJointsFrontLegs(outFile);
	SendJointsBackLegs(outFile);
}

void GA::SendJointsFrontLegs(ofstream *outFile) {

	(*outFile) << "\n( MainBody_LeftFrontUpperLeg\n";
	(*outFile) << "-connect MainBody LeftFrontUpperLeg\n";
	(*outFile) << "-jointPosition "	<< -BODY_WIDTH/2.0 -LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH -3*(TAR_OBJ_HEIGHT/4.0) <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";

	(*outFile) << "\n( MainBody_RightFrontUpperLeg\n";
	(*outFile) << "-connect MainBody RightFrontUpperLeg\n";
	(*outFile) << "-jointPosition "	<< BODY_WIDTH/2.0 +LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH  -3*(TAR_OBJ_HEIGHT/4.0)<<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";



	(*outFile) << "\n( LeftFrontUpperLeg_LeftFrontLeg\n";
	(*outFile) << "-connect LeftFrontUpperLeg LeftFrontLeg\n";
	(*outFile) << "-jointPosition "	<< -BODY_WIDTH/2.0 -LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH -(TAR_OBJ_HEIGHT/4.0) <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";

	(*outFile) << "\n( RightFrontUpperLeg_RightFrontLeg\n";
	(*outFile) << "-connect RightFrontUpperLeg RightFrontLeg\n";
	(*outFile) << "-jointPosition "	<< BODY_WIDTH/2.0 +LEG_RADIUS<<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH -(TAR_OBJ_HEIGHT/4.0) <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";
}

void GA::SendJointsBackLegs(ofstream *outFile) {

	(*outFile) << "\n( MainBody_LeftBackUpperLeg\n";
	(*outFile) << "-connect MainBody LeftBackUpperLeg\n";
	(*outFile) << "-jointPosition "	<< -BODY_WIDTH/2.0 -LEG_RADIUS<<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH - (BODY_LENGTH) <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";

	(*outFile) << "\n( MainBody_RightBackUpperLeg\n";
	(*outFile) << "-connect MainBody RightBackUpperLeg\n";
	(*outFile) << "-jointPosition "	<< BODY_WIDTH/2.0 +LEG_RADIUS<<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH - (BODY_LENGTH) <<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";


	(*outFile) << "\n( LeftBackUpperLeg_LeftBackLeg\n";
	(*outFile) << "-connect LeftBackUpperLeg LeftBackLeg\n";
	(*outFile) << "-jointPosition "	<< -BODY_WIDTH/2.0 -LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH - (BODY_LENGTH) -(TAR_OBJ_HEIGHT/2.0)<<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";
	(*outFile) << ")\n";

	(*outFile) << "\n( RightBackUpperLeg_RightBackLeg\n";
	(*outFile) << "-connect RightBackUpperLeg RightBackLeg\n";
	(*outFile) << "-jointPosition "	<< BODY_WIDTH/2.0 +LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH - (BODY_LENGTH) -(TAR_OBJ_HEIGHT/2.0)<<" \n";
	(*outFile) << "-jointType Hinge\n";
	(*outFile) << "-jointNormal 1 0 0\n";;
	(*outFile) << "-jointLimits -"<<LEG_EXTENSION_MAX<<" "<<LEG_EXTENSION_MAX<<"\n";
	(*outFile) << "-addMotor\n";
	(*outFile) << "-motorForce "<<MOTOR_LEG_MAX_FORCE<<"\n";
	(*outFile) << "-motorSpeed "<<MOTOR_SPEED<<"\n";;
	(*outFile) << ")\n";
}

void GA::SendJointsSensorNubs(ofstream *outFile) {

	(*outFile) << "\n( MainBody_SensorNubUpper\n";
	(*outFile) << "-connect MainBody SensorNubUpper\n";
	(*outFile) << "-jointPosition "	<< 0<<" "
				 	<< TAR_OBJ_HEIGHT/2.0 + (BODY_DEPTH/2) << " "
					<< -1.5*TAR_OBJ_WIDTH - (BODY_LENGTH/4.0) <<" \n";
	(*outFile) << "-jointType Fixed\n";
	(*outFile) << ")\n";
}

void GA::SendLegs(ofstream *outFile) {

	(*outFile) << "\n( LeftFrontLeg \n";
	(*outFile) << "-position "	<< -BODY_WIDTH/2.0 - LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/4.0 + LEG_RADIUS << " "
					<< -1.5*TAR_OBJ_WIDTH -(TAR_OBJ_HEIGHT/4.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 1 0\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";

	(*outFile) << "\n( RightFrontLeg \n";
	(*outFile) << "-position "	<< BODY_WIDTH/2.0 + LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/4.0 + LEG_RADIUS << " "
					<< -1.5*TAR_OBJ_WIDTH -(TAR_OBJ_HEIGHT/4.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 1 0\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";


	(*outFile) << "\n( LeftBackLeg \n";
	(*outFile) << "-position "	<< -BODY_WIDTH/2.0 - LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/4.0 + LEG_RADIUS << " "
					<< -1.5*TAR_OBJ_WIDTH - BODY_LENGTH -(TAR_OBJ_HEIGHT/2.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 1 0\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";

	(*outFile) << "\n( RightBackLeg \n";
	(*outFile) << "-position "	<< BODY_WIDTH/2.0  + LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/4.0 + LEG_RADIUS << " "
					<< -1.5*TAR_OBJ_WIDTH - BODY_LENGTH -(TAR_OBJ_HEIGHT/2.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 1 0\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";
}

void GA::SendMainBody(ofstream *outFile) {

	(*outFile) << "\n( MainBody \n";
	(*outFile) << "-position 0 " 	<< TAR_OBJ_HEIGHT/2.0 << " "
				     	<< -1.5*TAR_OBJ_WIDTH - (BODY_LENGTH/2.0) <<" \n";

	(*outFile) << "-shape -rectangle "	<<BODY_LENGTH<<" "
						<<BODY_WIDTH<<" "
						<<BODY_DEPTH<<" \n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 1 0 0 \n";
	(*outFile) << ") \n";
}

void GA::SendPostscript(ofstream *outFile) {

	(*outFile) << "\n( \n";
	(*outFile) << "-evaluationPeriod "<<evaluationLength<<" \n";
	(*outFile) << "-testForExplosions \n";
	(*outFile) << ") \n";
}

void GA::SendSensorNubs(ofstream *outFile) {

	(*outFile) << "\n( SensorNubUpper \n";
	(*outFile) << "-position 0 " 	<< TAR_OBJ_HEIGHT/2.0 + (BODY_DEPTH/2) << " "
				     	<< -1.5*TAR_OBJ_WIDTH - (BODY_LENGTH/4.0) <<" \n";

	(*outFile) << "-shape -sphere "	<<NUB_RADIUS<<"\n";
	(*outFile) << "-addDistanceSensor TargetObject "<<DIST_SENSOR_MAX_RANGE<<"\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0.5 0.5 0.5 \n";
	(*outFile) << ") \n";
}

void GA::SendTargetObject(ofstream *outFile) {

	(*outFile) << "\n( TargetObject \n";
	(*outFile) << "-position " << "0 " 
                                   << TAR_OBJ_HEIGHT/2.0  << " "
                                   << distOfTarget << " "
				   << "\n";
	(*outFile) << "-shape -rectangle "	<<TAR_OBJ_WIDTH<<" "
						<<TAR_OBJ_WIDTH<<" "
						<<TAR_OBJ_HEIGHT<<" \n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 0 1 \n";
	(*outFile) << "-floorContact \n";
	(*outFile) << ") \n";
}

void GA::SendUpperLegs(ofstream *outFile) {

	(*outFile) << "\n( LeftFrontUpperLeg \n";
	(*outFile) << "-position "	<< -BODY_WIDTH/2.0 -LEG_RADIUS<<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH  -(TAR_OBJ_HEIGHT/2.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 0 1\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << ") \n";

	(*outFile) << "\n( RightFrontUpperLeg \n";
	(*outFile) << "-position "	<< BODY_WIDTH/2.0 +LEG_RADIUS<<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH  -(TAR_OBJ_HEIGHT/2.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 0 1\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << ") \n";


	(*outFile) << "\n( LeftBackUpperLeg \n";
	(*outFile) << "-position "	<< -BODY_WIDTH/2.0 -LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH - BODY_LENGTH  -(TAR_OBJ_HEIGHT/4.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 0 1\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << ") \n";

	(*outFile) << "\n( RightBackUpperLeg \n";
	(*outFile) << "-position "	<< BODY_WIDTH/2.0 +LEG_RADIUS <<" "
				 	<< TAR_OBJ_HEIGHT/2.0 << " "
					<< -1.5*TAR_OBJ_WIDTH - BODY_LENGTH  -(TAR_OBJ_HEIGHT/4.0)<<" \n";
	(*outFile) << "-shape -cylinder "	<<LEG_RADIUS<< " " << (TAR_OBJ_HEIGHT/2.0) << "\n";
	(*outFile) << "-rotation 0 0 1\n";
	(*outFile) << "-mass 1 \n";
	(*outFile) << "-colour 0 1 0 \n";
	(*outFile) << ") \n";
}

void GA::WaitForSensorReadings(void) {

	simParams->WaitForFile(simParams->sensorFileName);
}

#endif
