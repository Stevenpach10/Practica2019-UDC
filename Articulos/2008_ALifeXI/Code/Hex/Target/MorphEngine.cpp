// MorphEngine.cpp : Defines the entry point for the console application.
//
#include "stdlib.h"

#include <ode/ode.h>
#include <drawstuff/drawstuff.h>

//#include <glut.h>

#include <time.h>
//#include <resource.h>
//#include <unistd.h>

#include "environment.h"
#include "simParams.h"

SIM_PARAMS  *simParams;
ENVIRONMENT *env;
dsFunctions fn;

extern int OUTPUT_RAYTRACER_FILE;
extern int ADD_NOISE;
extern int SPHERE;
extern double STEP_SIZE;

char locase (char c)
{
  if (c >= 'A' && c <= 'Z')
	  return c - ('a'-'A');
  else
	  return c;
}

static void start(void) {

}

void CaptureFrame(int num)
{

	/*
	int width = 352*2;
	int height = 288*2;

	fprintf(stderr,"capturing frame %04d\n",num);

   char s[100];
   sprintf (s,"frame/%d.ppm",num);
   FILE *f = fopen (s,"wb");
   fprintf (f,"P6\n%d %d\n255\n",width,height);

   void *buf = malloc( width * height * 3 );
   glReadPixels( 0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, buf );

   for (int y=(height - 1); y>=0; y--) {
     for (int x=0; x<width; x++) {
       unsigned char *pixel = ((unsigned char *)buf)+((y*width+ x)*3);
       unsigned char b[3];
       b[0] = *pixel;
       b[1] = *(pixel+1);
       b[2] = *(pixel+2);
       fwrite(b,3,1,f);
     }
    }
   free(buf);
   fclose(f);
   */
}

int BothObjectsAreClawTips(dGeomID o1, dGeomID o2) {

	ME_OBJECT *obj1 = (ME_OBJECT *)dGeomGetData(o1);
	int c1 = obj1 && (strcmp(obj1->name,"LeftClawTip")==0);

	ME_OBJECT *obj2 = (ME_OBJECT *)dGeomGetData(o2);
	int c2 = obj2 && (strcmp(obj2->name,"RightClawTip")==0);

	obj1 = NULL;
	obj2 = NULL;

	return( c1 && c2 );
}

int OneObjectIsGround(dGeomID o1, dGeomID o2) {

	int g1 = (o1 == env->floor );
	int g2 = (o2 == env->floor);
	return( g1 || g2 );
}

int OneObjectIsTarget(dGeomID o1, dGeomID o2) {

	ME_OBJECT *obj1 = (ME_OBJECT *)dGeomGetData(o1);
	int t1 = (o2!=env->floor) && obj1 && (strcmp(obj1->name,"TargetObject")==0);

	ME_OBJECT *obj2 = (ME_OBJECT *)dGeomGetData(o2);
	int t2 = (o1!=env->floor) && obj2 && (strcmp(obj2->name,"TargetObject")==0);

	obj1 = NULL;
	obj2 = NULL;

	return( t1 || t2 );
}

int CanInterpenetrate(dGeomID o1, dGeomID o2) {

	if ( OneObjectIsGround(o1,o2) )
		return( false );

	if ( OneObjectIsTarget(o1,o2) )
		return( false );

	if ( BothObjectsAreClawTips(o1,o2) )
		return( false );

	return( true );
}

void SetTouchSensors(dGeomID o1, dGeomID o2) {

	ME_OBJECT *obj;
	obj = (ME_OBJECT *)dGeomGetData(o1);
	if ( obj && (obj->touchSensorID>-1) )
		obj->nn->SetTouchSensor(obj->touchSensorID);
	obj = (ME_OBJECT *)dGeomGetData(o2);
	if ( obj && (obj->touchSensorID>-1) )
		obj->nn->SetTouchSensor(obj->touchSensorID);
}

void SeekInvalidCollisions(dGeomID o1) {

	ME_OBJECT *obj = (ME_OBJECT *)dGeomGetData(o1);
	if ( obj ) {
		const dReal *vel = dBodyGetLinearVel(obj->body);
		if ( (fabs(vel[0])>10.0) || (fabs(vel[0])>10.0) || (fabs(vel[0])>10.0) )
			env->invalidPhysics = true;
	}
}

static void nearCallback(void *data, dGeomID o1, dGeomID o2) {

	int i,n;

	if ( CanInterpenetrate(o1,o2) )
		return;

	const int N = 32;
	dContact contact[N];
	n = dCollide (o1,o2,N,&contact[0].geom,sizeof(dContact));
	if (n > 0) {

		SetTouchSensors(o1,o2);
		SeekInvalidCollisions(o1);

		for (i=0; i<n; i++) {

			contact[i].surface.slip1 = 0.01;
			contact[i].surface.slip2 = 0.01;
			contact[i].surface.mode = dContactSoftERP | 
						dContactSoftCFM | 
						dContactApprox1 | 
						dContactSlip1 | dContactSlip2;
			contact[i].surface.mu = 50.0; // was: dInfinity
			contact[i].surface.soft_erp = 0.96;
			contact[i].surface.soft_cfm = 0.01;

			dJointID c = dJointCreateContact (env->world,env->contactgroup,&contact[i]);
			dJointAttach (c,
			dGeomGetBody(contact[i].geom.g1),
			dGeomGetBody(contact[i].geom.g2));
		}
	}
}

void SetViewpoint(void) {

		float xyz[3];
		float hpr[3];

		/*
		dsGetViewpoint(xyz,hpr);

		printf("%3.3f %3.3f %3.3f %3.3f %3.3f %3.3f\n",
			xyz[0],xyz[1],xyz[2],hpr[0],hpr[1],hpr[2]);
		*/

		xyz[0] = 1.31;
		xyz[1] = 0.996;
		xyz[2] = 1.46;

		hpr[0] = -132.5;
		hpr[1] = -48.0;
		hpr[2] = 0.0;

		dsSetViewpoint(xyz,hpr);
}

void Tick(int pause, int shouldDraw) {

	if ( simParams->evaluating ) {

		if ( shouldDraw ) {
			env->Draw();
			//SetViewpoint();

			if ( (simParams->recordMovie) && (simParams->internalTimer%10==0) )
				CaptureFrame(simParams->currFrame++);
		}

		if ( !pause ) {

			dSpaceCollide(env->space,0,&nearCallback);
			dWorldStep(env->world,STEP_SIZE);
			dJointGroupEmpty(env->contactgroup);

			env->MoveAgents();

			if ( env->EvaluationFinished() ) {

				env->DestroyAgent();
				env->Reset();
				simParams->agentsToEvaluate--;

				if ( simParams->forwardPlayback )
					simParams->indexToPlayback++;

				if ( simParams->agentsToEvaluate == 0 ) {
					simParams->CloseFiles();
					simParams->evaluating = false;
				}
				else
					env->CreateAgent();
			}
		}
	}

	else {

		if ( env->AgentAvailable() ) {
			simParams->OpenFiles();
			env->CreateAgent();
			simParams->evaluating = true;
		}
	}
}

static void simLoop(int pause) {

	Tick(pause,true);
}

static void command(int cmd) {

	cmd = locase(cmd);

	switch ( cmd ) {

	case '8':
		env->Push(0.0,0.0,1.0);
		break;

	case '2':
		env->Push(0.0,0.0,-1.0);
		break;

	case '9':
		env->Push(-1.0,0.0,0.0);
		break;

	case '1':
		env->Push(1.0,0.0,0.0);
		break;

	case '4':
		env->Push(0.0,-1.0,0.0);
		break;

	case '6':
		env->Push(0.0,1.0,0.0);
		break;

	case 'd':
		env->ChangeDebrisField();
		break;

	case 'f':
		env->ToggleFootprintDrawing();
		break;

	case 'm':
		printf("Recording movie.\n");
		simParams->recordMovie = true;
		break;

	case 'n':
		simParams->drawNetwork++;
		if ( simParams->drawNetwork == 3 )
			simParams->drawNetwork = 0;
		break;

	case 'c':
		if ( env->plume )
			env->DestroyPlume();
		else
			env->CreatePlume();
		break;

	case 'p':
		env->IncreasePerturbation(0.1);
		break;

	case 'r':
		env->ToggleTrajectoryDrawing();
		break;

	case 's':
		env->PerturbSynapses();
		break;

	case 't':
		simParams->useTransparency = !simParams->useTransparency;
		break;

	case 'x':
		exit(0);
		break;
	}
}

void InitializeODE(int argc, char **argv) {

	fn.version = DS_VERSION;
	fn.start = &start;
	fn.step = &simLoop;
	fn.command = &command;
	fn.stop = 0;
	fn.path_to_textures = "textures";
}

int main(int argc, char **argv)
{
/*
        clock_t endwait;
        endwait = clock() + clock_t(2.0*CLOCKS_PER_SEC);
        while (clock() < endwait) {}
	printf("Finished waiting.\n");
*/
	simParams = new SIM_PARAMS(argc, argv);

	if ( simParams->rendering )
		InitializeODE(argc,argv);

	env = new ENVIRONMENT;

	if ( simParams->rendering ) {
		dsSimulationLoop(argc,argv,352,288,&fn);
		//dsSimulationLoop(argc,argv,352*2,288*2,&fn);
	}
	else {

		while ( 1 ) {

			Tick(false,false);
		}
	}

	delete env;
	env = NULL;

	delete simParams;
	simParams = NULL;

	return 0;
}
