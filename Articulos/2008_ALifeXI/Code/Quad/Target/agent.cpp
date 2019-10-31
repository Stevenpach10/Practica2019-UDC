/* ---------------------------------------------------
   FILE:     agent.cpp
	AUTHOR:   Josh Bongard
	DATE:     February 19, 2002
	FUNCTION: This class contains all information for
				 a single agent.
 -------------------------------------------------- */

#include <drawstuff/drawstuff.h>

#ifndef _AGENT_CPP
#define _AGENT_CPP

#include "agent.h"
#include "simParams.h"
#include "math.h"

extern int OUTPUT_FOOTPRINTS;
extern int OUTPUT_TRAJECTORY;
extern int CREATE_PLUME;
extern double GROUND_LENGTH;
extern int RANDOM_DISPERSAL;
extern double DISP_PTS[16];
extern int			JOINT_SPRING;
extern int	JOINT_HINGE;
extern int  CYLINDER;
extern int  SPHERE;

extern char BODY_FILENAME[50];
extern char BRAIN_FILENAME[50];
extern char OBJECT_FILENAME[50];
extern char SENSOR_FILENAME[50];

extern SIM_PARAMS *simParams;

AGENT::AGENT(int IDNum, dWorldID world, dSpaceID space) {

	ID = IDNum;
	timeRemainingUntilNextMotorCommand = 10;

	trajectory = NULL;
	targetObject = NULL;
	totalMass = 0.0;
	totalVolume = 0.0;

	CreateBrain();

	CreateBody(world,space);

	network->CreateSensors();

	ReadInDataParameters();

	sensorValues = new MATRIX(simParams->evalPeriod,network->numInput,0.0);
}

AGENT::AGENT(int IDNum, AGENT *templateAgent) {

/*
	ID = IDNum;
	numObjects = templateAgent->numObjects;
	numJoints = templateAgent->numJoints;
	hiddenNodes = templateAgent->hiddenNodes;
	numMorphParams = templateAgent->numMorphParams;
	trajectory = NULL;

	if ( RANDOM_DISPERSAL ) {
		displacement[0] = simParams->Rand((-GROUND_LENGTH/2.0)*simParams->displacementDistance,
													 (GROUND_LENGTH/2.0)*simParams->displacementDistance);
		displacement[1] = simParams->Rand((-GROUND_LENGTH/2.0)*simParams->displacementDistance,
													 (GROUND_LENGTH/2.0)*simParams->displacementDistance);
	}
	else {
		displacement[0] = DISP_PTS[(ID-1)*2] * (GROUND_LENGTH/2.0)*simParams->displacementDistance;
		displacement[1] = DISP_PTS[(ID-1)*2+1] * (GROUND_LENGTH/2.0)*simParams->displacementDistance;
	}

	objects = new ME_OBJECT * [numObjects];
	joints  = new ME_JOINT  * [numJoints];
	network = new NEURAL_NETWORK;

	int currObj;
	for (currObj=0;currObj<numObjects;currObj++)
		objects[currObj] = new ME_OBJECT(this,templateAgent->objects[currObj],displacement,network);

	for (currObj=0;currObj<numObjects;currObj++)
		objects[currObj]->FindOtherObjects(numObjects,objects);

	int currJoint;
	for (currJoint=0;currJoint<numJoints;currJoint++)
		joints[currJoint] = new ME_JOINT(ID,objects,numObjects,displacement,
												 templateAgent->joints[currJoint],network);

	FindRelatedJoints();

	//network->Init(hiddenNodes,templateAgent->network->isReactive);
*/
}

AGENT::~AGENT(void) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)
		delete objects[currObject];

	int currJoint;

	for (currJoint=0;currJoint<numJoints;currJoint++)
		delete joints[currJoint];

	if ( trajectory ) {

		delete trajectory;
		trajectory = NULL;
	}

	targetObject = NULL;

//	sensorValues->PrintRow(simParams->internalTimer-1);

	if ( Stopped() )
		sensorValues->WriteRows(simParams->internalTimer,simParams->sensorFile);
	else
		sensorValues->Write(simParams->sensorFile);

	delete[] objects;
	objects = NULL;

	delete[] joints;
	joints = NULL;

	delete sensorValues;
	sensorValues = NULL;
}

int  AGENT::AttachedTo(AGENT *otherAgent) {

	if ( numOfExternalJoints==0 )
		if ( otherAgent->numOfExternalJoints==0 )
			return( false );
		else
			return( otherAgent->AttachedTo(this) );
	else {
		int currExtJoint = 0;
		int extJointToOtherAgent = false;

		while ( (currExtJoint<numOfExternalJoints) && (!extJointToOtherAgent) ) {

			if ( externalJoints[currExtJoint]->AttachesTo(ID,otherAgent->ID) )
				extJointToOtherAgent = true;
			currExtJoint++;
		}
		return( extJointToOtherAgent );
	}
}

void AGENT::AttachTo(AGENT *otherAgent, dWorldID world) {

	/*
	ME_OBJECT *firstObj, *secondObj;

	firstObj = (ME_OBJECT *)McdModelGetUserData(result.pair->model1);
	secondObj = (ME_OBJECT *)McdModelGetUserData(result.pair->model2);

	externalJoints[numOfExternalJoints] = new ME_JOINT(numOfExternalJoints,ID,firstObj,secondObj);
	externalJoints[numOfExternalJoints]->Attach(world);
	numOfExternalJoints++;
	*/
}

int  AGENT::ContainsLightSensor(void) {

	int containsLightSensor = false;
	int objIndex = 0;

	while ( (objIndex < numObjects) && (!containsLightSensor) ) {
		if ( objects[objIndex]->lightSensorID > -1 )
			containsLightSensor = true;
		objIndex++;
	}

	return( containsLightSensor );

}

void AGENT::CreateJoints(dWorldID world) {

	int currJoint;

	for (currJoint=0;currJoint<numJoints;currJoint++)
		joints[currJoint]->CreateODEStuff(world);
}

void AGENT::CreateObjects(int genomeLength, double *genes, ME_OBJECT *lightSource,
								  dWorldID world, dSpaceID space) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)

		objects[currObject]->CreateODEStuff(world,space);

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->DisableContacts();

	if ( lightSource != NULL )
		DetermineMaxLightSensorReading(lightSource);
}

void AGENT::CreateODEStuff(dWorldID world, dSpaceID space) {

	int currObject, currJoint;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->CreateODEStuff(world,space);

	for (currJoint=0;currJoint<numJoints;currJoint++)
		joints[currJoint]->CreateODEStuff(world);
}

void AGENT::DestroyODEStuff(dSpaceID space) {

	int currObject;
	int currJoint;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->DestroyODEStuff(space);

	for (currJoint=0;currJoint<numJoints;currJoint++)
		joints[currJoint]->DestroyODEStuff();
}

double AGENT::DistTo(int objIndex, AGENT *otherAgent) {

	double myPos[3], myRot[12], otherPos[3], otherRot[12];
	ME_OBJECT *otherObj;

	objects[objIndex]->GetPosAndRot(myPos,myRot);

	otherObj = otherAgent->GetObject(objIndex);
	otherObj->GetPosAndRot(otherPos,otherRot);

	return( simParams->DistBetween(myPos,otherPos) );
}

void AGENT::Draw(void) {

	int currObject, currJoint;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->Draw();

	//for (currJoint=0;currJoint<numJoints;currJoint++)
	//	joints[currJoint]->Draw();

	if ( trajectory )
		trajectory->Draw(1.0,1.0,1.0);

	if ( simParams->drawNetwork )
		DrawNeuralNetwork();
}

int  AGENT::Exploding(void) {

	int j = 0;
	int exploding = false;

	while ( (j<numJoints) && (!exploding) ) {
		exploding = joints[j]->Separated();
		j++;
	}

	j = 0;
	while ( (j<numObjects) && (!exploding) ) {
		exploding = objects[j]->BeyondRange();
		j++;
	}

	return( exploding );
}

void AGENT::GetCentreOfMass(double *com) {

	int currObject;
	double pos[3], rot[12];

	com[0] = 0.0;
	com[1] = 0.0;
	com[2] = 0.0;

	for (currObject=0;currObject<numObjects;currObject++) {

		objects[currObject]->GetPosAndRot(pos,rot);

		com[0] = com[0] + pos[0];
		com[1] = com[1] + pos[1];
		com[2] = com[2] + pos[2];
	}

	com[0] = com[0] / (numObjects);
	com[1] = com[1] / (numObjects);
	com[2] = com[2] / (numObjects);
}

int AGENT::GetID(void) {

	return(ID);
}

ME_JOINT *AGENT::GetJoint(int jointIndex) {

	return( joints[jointIndex] );
}

ME_JOINT *AGENT::GetJoint(char *jointName) {

	int jointFound = false;
	int jointIndex = 0;

	while ( (jointIndex<numJoints) && (!jointFound) ) {

		jointFound = joints[jointIndex]->IsMyName(jointName);
		if ( !jointFound )
			jointIndex++;
	}

	if ( jointFound == false )
		return( NULL );
	else
		return( joints[jointIndex] );
}

double AGENT::GetMaxHeight(void) {

	double maxHeight = -100.0;

	int currObject;
	double currObjHeight;

	for (currObject=0;currObject<numObjects;currObject++) {

		currObjHeight = objects[currObject]->GetHeight();

		if ( currObjHeight > maxHeight )
			maxHeight = currObjHeight;
	}

	return( maxHeight );
}

double AGENT::GetMinHeight(void) {

	double minHeight = 100.0;

	int currObject;
	double currObjHeight;

	for (currObject=0;currObject<numObjects;currObject++) {

		if ( objects[currObject]->objectType != CYLINDER ) {

			currObjHeight = objects[currObject]->GetHeight();

			if ( currObjHeight < minHeight )
				minHeight = currObjHeight;
		}
	}

	return( minHeight );
}

char *AGENT::GetName(int objIndex) {

	return( objects[objIndex]->name );
}

int  AGENT::GetNumOfJoints(void) {

	return( numJoints );
}

int  AGENT::GetNumOfObjects(void) {

	return( numObjects );
}

int  AGENT::GetNumOfPossibleJoints(void) {

	return( numJoints + numOfPossibleExternalJoints );
}

int  AGENT::GetNumOfWeights(void) {

	//return( network->numWeights );

	return( 0 );
}

ME_OBJECT *AGENT::GetObject(int objIndex) {

	return( objects[objIndex] );
}

double AGENT::GetWidth(void) {

	double minWidth = 100.0;
	double maxWidth = -100.0;

	double pos[3];
	double rot[12];

	for (int i=0;i<numObjects;i++) {

		objects[i]->GetPosAndRot(pos,rot);

		if ( pos[0] < minWidth )
			minWidth = pos[0];

		if ( pos[0] > maxWidth )
			maxWidth = pos[0];
	}

	return( maxWidth - minWidth );
}

double AGENT::GetLength(void) {

	double minLength = 100.0;
	double maxLength = -100.0;

	double pos[3];
	double rot[12];

	for (int i=0;i<numObjects;i++) {

		objects[i]->GetPosAndRot(pos,rot);

		if ( pos[1] < minLength )
			minLength = pos[1];

		if ( pos[1] > maxLength )
			maxLength = pos[1];
	}

	return( maxLength - minLength );
}

void AGENT::HandleCollisions(int internalTimer) {

	/*
	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)
		
		network->UpdateSensorValue(1.0,objects[currObject]->touchSensorID );
	*/
}

void AGENT::IncreasePerturbation(double amt) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)
		
		objects[currObject]->IncreasePerturbation(amt);
}

void AGENT::InitNetwork(int hiddenN, int useReactiveController) {

	/*
	hiddenNodes = hiddenN;
	network->Init(hiddenNodes,useReactiveController);
	*/
}

void AGENT::Move(int numOfAgents, ME_OBJECT *lightSource, PLUME *plume, dWorldID world, dGeomID floor) {

	TakeSensorReadings();

	for (int i=0;i<1;i++)
		network->Update();

	ActuateJoints();
	network->ResetSensors();
}

void AGENT::PerturbSynapses(void) {

	//network->PerturbSynapses();
}

void AGENT::Push(double x, double y, double z) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->Push(x,y,z);
}

void AGENT::RemoveExtraneousObjects(dSpaceID space) {

	/*
	int j;
	ME_OBJECT *targettedObj;

	for (j=0;j<numJoints;j++) {
		targettedObj = joints[j]->GeomTransformPossible();
		if ( targettedObj != NULL )
			targettedObj->SwitchToGeomTransform(joints[j]->ComplementaryObj(targettedObj),space);
	}
	*/
}

void AGENT::Reset(void) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->Reset();
}

void AGENT::SaveToRaytracerFile(ofstream *outFile) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->SaveToRaytracerFile(outFile);
}

void AGENT::SpecifyPhenotype(int genomeLength, double *genes) {

	//network->LabelSynapses(genomeLength,genes,numMorphParams);
	//network->ClearValues();

	int currObject, currJoint;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->SetEvolvableParams(numMorphParams,genomeLength,genes);
	
	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->SetParamsBasedOnOtherObjects();

	for (currJoint=0;currJoint<numJoints;currJoint++)
		joints[currJoint]->ResetPosition();

}

int  AGENT::Stopped(void) {

	return( objects[1]->Stopped() );
}

void AGENT::SwitchOnPressureSensors(dWorldID world) {

	for (int currJoint=0;currJoint<numJoints;currJoint++)
		joints[currJoint]->SwitchOnPressureSensor(world);
}

void AGENT::ToggleFootprintDrawing(void) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)
		objects[currObject]->ToggleFootprintDrawing();
}

void AGENT::ToggleTrajectoryDrawing(void) {

	if ( !trajectory )
		trajectory = new TRAJECTORY(simParams->evalPeriod);
	else {
		delete trajectory;
		trajectory = NULL;
	}
}

// ----------------------------------------------------------------
//                           Private methods
// ----------------------------------------------------------------

void AGENT::ActuateJoints(void) {

	int currJoint;
	double motorPosition;

	int currMotorizedJoint = 0;

	for (currJoint=0;currJoint<numJoints;currJoint++)
		if ( joints[currJoint]->motorNeuronID > -1 ) {

			int neuronIndex = joints[currJoint]->motorNeuronID;
			motorPosition = network->GetNeuronOutput(neuronIndex);
			motorPosition = motorPosition*(joints[currJoint]->upperLimit-joints[currJoint]->lowerLimit);
			motorPosition = motorPosition + joints[currJoint]->lowerLimit;
			motorPosition = motorPosition*0.95;

			joints[currJoint]->Actuate( motorPosition );
		}
}

void AGENT::BreakExternalConnectionsIfNecessary(void) {

	int currJoint = 0;
	int jointsToProcess;

	while ( currJoint<numOfExternalJoints ) {

		if ( externalJoints[currJoint]->IsBreaking() ) {
			
			externalJoints[currJoint]->Break();
			delete externalJoints[currJoint];
			externalJoints[currJoint] = NULL;

			for (jointsToProcess=currJoint+1;jointsToProcess<numOfExternalJoints;jointsToProcess++)
				externalJoints[jointsToProcess-1] = externalJoints[jointsToProcess];
			numOfExternalJoints--;
		}
		else
			currJoint++;
	}
}

int  AGENT::CountPossibleExternalJoints(void) {

	int possibleJoints = 0;
	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)

		if ( objects[currObject]->isAttacher )
			possibleJoints++;

	return( possibleJoints );
}

void AGENT::CreateBody(dWorldID world, dSpaceID space) {

	(*simParams->bodyFile) >> numObjects;
	(*simParams->bodyFile) >> numJoints;

	if ( !simParams->connectedObjects )
		simParams->connectedObjects = new MATRIX(numObjects,numObjects,0.0);
	else
		simParams->connectedObjects->SetAllTo(0);

	objects = new ME_OBJECT * [numObjects];
	joints  = new ME_JOINT  * [numJoints];

	for (int o=0;o<numObjects;o++)
		ReadInObject(o);

	for (int currObj=0;currObj<numObjects;currObj++)
		objects[currObj]->FindOtherObjects(numObjects,objects);

	for (int j=0;j<numJoints;j++)
		ReadInJoint(j);

	CreateODEStuff(world,space);
}

void AGENT::CreateBrain(void) {

	network = new NEURAL_NETWORK(	simParams->tauFile,simParams->weightFile,
					simParams->omegaFile,simParams->sensorWFile);
}

void AGENT::DetachJoints(void) {

	int currJoint = 0;
	int jointsToProcess;

	while ( currJoint<numOfExternalJoints ) {

		if ( externalJoints[currJoint]->BreakageDesired(network) ) {
			
			externalJoints[currJoint]->Break();
			delete externalJoints[currJoint];
			externalJoints[currJoint] = NULL;

			for (jointsToProcess=currJoint+1;jointsToProcess<numOfExternalJoints;jointsToProcess++)
				externalJoints[jointsToProcess-1] = externalJoints[jointsToProcess];
			numOfExternalJoints--;
		}
		else
			currJoint++;
	}
}

void AGENT::DetermineMaxLightSensorReading(ME_OBJECT *lightSource) {

	int currObject;
	double maxDistance = -1.0;
	double tempDist;

	for (currObject=0;currObject<numObjects;currObject++) {
	
		tempDist = objects[currObject]->GetDistance(lightSource);

		if ( tempDist > maxDistance )
			maxDistance = tempDist;
	}

	maxLightSensorReading = maxDistance;
}

void AGENT::DrawJointNormals(void) {

	int currJoint;

	for (currJoint=0;currJoint<numJoints;currJoint++)
		joints[currJoint]->DrawNormals();
}

void AGENT::DrawNeuralNetwork(void) {

	/*
	if ( simParams->drawNetwork == 1 ) {
		double com[3];
		GetCentreOfMass(com);
		network->DrawNeurons(com);
	}
	else {

		double maxHeight = GetMaxHeight();

		int currObject;
		for (currObject=0;currObject<numObjects;currObject++)
			objects[currObject]->DrawSensorNeurons(maxHeight,3.0);

		int currJoint;
		for (currJoint=0;currJoint<numJoints;currJoint++) {
			joints[currJoint]->DrawSensorNeurons(maxHeight,2.0);
			joints[currJoint]->DrawMotorNeurons(maxHeight,1.0);
		}
	}
	*/
}

void AGENT::FindRelatedJoints(void) {

	int currJoint;
	ME_JOINT *relatedJoint;

	for (currJoint=0;currJoint<numJoints;currJoint++) {

		if ( joints[currJoint]->RelatedToOtherJoint() ) {
			relatedJoint = GetJoint(joints[currJoint]->GetRelatedJointName());
			joints[currJoint]->SetRelatedJoint(relatedJoint);
		}
	}
}

void AGENT::IntroduceNoise(void) {

	int currObject;

	for (currObject=0;currObject<numObjects;currObject++)

		objects[currObject]->IntroduceNoise();
}

void AGENT::PrintObjectPositions(void) {

	double pos[3], rot[12];

		objects[0]->GetPosAndRot(pos,rot);
		for (int i=0;i<3;i++)
			printf("%3.3f ",pos[i]);
		printf("\n");
}

void AGENT::ReadInDataParameters(void) {

	char readIn[50];

	(*simParams->bodyFile) >> readIn;
	
	if ( strcmp(readIn,"(") != 0 ) {
		printf("Read in error: expecting opening bracket.\n");
		char ch = getchar();
		exit(0);
	}

	(*simParams->bodyFile) >> readIn;

	while ( strcmp(readIn,")") != 0 ) {

		if ( strcmp(readIn,"-evaluationPeriod") == 0 ) {

			(*simParams->bodyFile) >> readIn;
			simParams->evalPeriod = atoi(readIn);
		}
		else
		if ( strcmp(readIn,"-testForExplosions") == 0 ) {
			simParams->testForExplosions = true;
		}

		(*simParams->bodyFile) >> readIn;
	}
}

void AGENT::ReadInJoint(int currJoint) {

	joints[currJoint] = new ME_JOINT(ID,objects,numObjects,joints,numJoints,simParams->bodyFile,currJoint,network);

	//FindRelatedJoints();
}

void AGENT::ReadInObject(int currObject) {

	objects[currObject] = new ME_OBJECT(this,numObjects,simParams->bodyFile,currObject,network,objects);

	/*
	for (currObject=0;currObject<numObjects;currObject++) {

		numMorphParams = numMorphParams + objects[currObject]->CountMorphParams(numMorphParams);
		objects[currObject]->FindOtherObjects(numObjects,objects);
	}
	*/
}

void AGENT::RecordObjectData(void) {

	/*
	double pos[3], rot[12];

	targetObject->GetPosAndRot(pos,rot);

	objectData->Set(simParams->internalTimer,0,pos[0]);
	objectData->Set(simParams->internalTimer,1,pos[1]);
	objectData->Set(simParams->internalTimer,2,pos[2]);
	*/
}

void AGENT::RecordSensorData(void) {

	/*
	for (int s=0;s<network->numInput;s++) {

		sensorData->Set(simParams->internalTimer,s,network->GetSensorValue(s));
	}
	*/

	/*
	double pos[3], rot[12];
	double pos2[3], rot2[12];
	double pos3[3], rot3[12];

	double distFromOrigin;

	int k = 0;
	int otherObject, otherObject2;

	for (int o=0;o<numObjects;o++) {

		objects[o]->GetPosAndRot(pos,rot);

		distFromOrigin = sqrt( pow(pos[0]-1.0,2.0) + pow(pos[1]-1.0,2.0) + pow(pos[2]-0.0,2.0) );
		sensorData->Set(simParams->internalTimer,k,distFromOrigin);

		/*
		distFromOrigin = sqrt( pow(pos[0]+1.0,2.0) + pow(pos[1]-1.0,2.0) + pow(pos[2]-0.0,2.0) );
		sensorData->Set(simParams->internalTimer,k+1,distFromOrigin);

		distFromOrigin = sqrt( pow(pos[0]-1.0,2.0) + pow(pos[1]+1.0,2.0) + pow(pos[2]-0.0,2.0) );
		sensorData->Set(simParams->internalTimer,k+2,distFromOrigin);

		distFromOrigin = sqrt( pow(pos[0]+1.0,2.0) + pow(pos[1]+1.0,2.0) + pow(pos[2]-0.0,2.0) );
		sensorData->Set(simParams->internalTimer,k+3,distFromOrigin);
		*/
		//k = k + 1;

		/*
		switch ( o ) {
		case 0:
			otherObject = 1;
			otherObject2 = 2;
			break;
		case 1:
			otherObject = 0;
			otherObject2 = 2;
			break;
		case 2:
			otherObject = 0;
			otherObject2 = 1;
			break;
		case 4:
			otherObject = 1;
			otherObject2 = 0;
			break;
		case 5:
			otherObject = 1;
			otherObject2 = 0;
			break;
		}

		objects[o]->GetPosAndRot(pos,rot);
		objects[otherObject]->GetPosAndRot(pos2,rot2);
		objects[otherObject2]->GetPosAndRot(pos3,rot3);

		distFromOrigin = sqrt( pow(pos[0]-pos2[0],2.0) + pow(pos[1]-pos2[1],2.0) + pow(pos[2]-pos2[2],2.0) );
		sensorData->Set(simParams->internalTimer,k,distFromOrigin);

		distFromOrigin = sqrt( pow(pos[0]-pos3[0],2.0) + pow(pos[1]-pos3[1],2.0) + pow(pos[2]-pos3[2],2.0) );
		sensorData->Set(simParams->internalTimer,k+1,distFromOrigin);

		k = k + 1;
		*/
	//}
}

void AGENT::RecordCentreOfMass(double *com) {

	(*simParams->trajectoryFile) << com[0] << ";";
	(*simParams->trajectoryFile) << com[1] << ";";
	(*simParams->trajectoryFile) << com[2] << "\n";
}

void AGENT::SaveCentreOfMass(double *com) {

	trajectory->x[simParams->internalTimer-1] = com[0];
	trajectory->y[simParams->internalTimer-1] = com[1];
	trajectory->z[simParams->internalTimer-1] = com[2];
}

void AGENT::TakeAgentSensorReadings(int numOfAgents) {

}

void AGENT::TakeAngleSensorReadings(void) {

	for (int j=0;j<numJoints;j++) {
		if ( joints[j]->sensorNeuronID>-1 ) {
			double angle = joints[j]->GetAngle()*180.0/3.14159;
			double jointRange = joints[j]->upperLimit*180/3.14159-joints[j]->lowerLimit*180/3.14159;
			angle = angle/jointRange + 0.5;
			network->sensors->Set(0,joints[j]->sensorNeuronID,angle);
			sensorValues->Set(simParams->internalTimer,joints[j]->sensorNeuronID,angle);
		}
	}
}

void AGENT::TakeAttachmentSensorReadings(void) {

}

void AGENT::TakeChemoSensorReadings(PLUME *plume) {

}

void AGENT::TakeDistanceSensorReading() {

	for (int i=0;i<numObjects;i++) {
		if ( objects[i]->distSensorID>-1 ) {
			double targetPos[3], targetRot[12];
			objects[i]->distSensorTarget->GetPosAndRot(targetPos,targetRot);
			double myPos[3], myRot[12];
			objects[i]->GetPosAndRot(myPos,myRot);
			double dist = sqrt( 	pow(targetPos[0]-myPos[0],2.0) + 
						pow(targetPos[1]-myPos[1],2.0) + 
						pow(targetPos[2]-myPos[2],2.0) );
			dist = (objects[i]->distSensorRange - dist) / objects[i]->distSensorRange;
			if ( dist<0 )
				dist = 0;
			network->sensors->Set(0,objects[i]->distSensorID,dist);
			sensorValues->Set(simParams->internalTimer,objects[i]->distSensorID,dist);
		}
	}
}

void AGENT::TakeLightSensorReadings(ME_OBJECT *lightSource) {

}

void AGENT::TakeLowestHeightSensorReading(void) {

	double lowestHeight = GetMinHeight();

	//printf("%3.3f\n",lowestHeight);

	sensorValues->Set(simParams->internalTimer,15,lowestHeight);
}

void AGENT::TakeObj0HeightSensorReading(void) {

	double obj0Height = objects[0]->GetHeight();

	//printf("%3.3f\n",lowestHeight);

	sensorValues->Set(simParams->internalTimer,sensorValues->width-1,obj0Height);
}

void AGENT::TakeOrientationSensorReadings(void) {

	objects[0]->SetOrientationSensors();
}

void AGENT::TakePressureSensorReadings(dGeomID floor) {

	ME_OBJECT *currObject;
	int currFoot = 0;
	dContact contact;
	double totalDepth = 0.0;
	double totalDepthNormalized;
	double indivWeight;

	for (int currObj=0;currObj<numObjects;currObj++) {

		currObject = objects[currObj];
		
		if ( (currObject->objectType == SPHERE) || (currObject->ID==0) ) {

			if (dCollide(currObject->geom,floor,0,&contact.geom,sizeof(dContactGeom))) {

				totalDepth = totalDepth + contact.geom.depth;
			}
		}
	}

	totalDepthNormalized = totalDepth/totalVolume;

	currObject = NULL;
}

void AGENT::TakeSensorReadings() {

	//TakeAngleSensorReadings();

	//TakePressureSensorReadings(floor);

	//TakeOrientationSensorReadings();

	//TakeHeightSensorReading();

	TakeTouchSensorReadings();

	TakeDistanceSensorReading();

	TakeAngleSensorReadings();

	//TakeVelocitySensorReadings();

	//TakeAgentSensorReadings(numOfAgents);

	//TakeObj0HeightSensorReading();

	//TakeTouchSensorReadings();

	//TakeLowestHeightSensorReading();

	//TakeLightSensorReadings(lightSource);
	
	//if ( plume )
	//	TakeChemoSensorReadings(plume);
}

void AGENT::TakeTouchSensorReadings(void) {

	for (int i=0;i<numObjects;i++) {
		if ( objects[i]->touchSensorID>-1 ) {
			double touching = network->sensors->Get(0,objects[i]->touchSensorID);
			sensorValues->Set(simParams->internalTimer,objects[i]->touchSensorID,touching);
		}
	}
}

void AGENT::TakeVelocitySensorReadings(void) {

	const dReal *vel =  dBodyGetLinearVel(objects[0]->body);

	double linearSpeed = sqrt( vel[0]*vel[0] + vel[1]*vel[1] + vel[2]*vel[2]);

	vel = dBodyGetAngularVel(objects[0]->body);

	double angularSpeed = sqrt( vel[0]*vel[0] + vel[1]*vel[1] + vel[2]*vel[2]);

	if ( isnan(linearSpeed+angularSpeed) ) {
		linearSpeed = 50.0;
		angularSpeed = 50.0;
	}

	sensorValues->Set(simParams->internalTimer,15,linearSpeed+angularSpeed);
}

void AGENT::UpdateSpringConnections(void) {

	int currJoint;

	for (currJoint=0;currJoint<numJoints;currJoint++)
		if ( joints[currJoint]->jointType == JOINT_SPRING )
			joints[currJoint]->UpdateSpring();
}

#endif
