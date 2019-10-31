from numpy import *
from pylab import *
          
def CompareCyclicities(figNo,alreadySaved,useQuad,useLarge):

     numRuns = 35;
     #numRuns = 2;
     
     dists = [0.0,0.5,1.0,1.5,2.0,2.5,3.0];
     #dists = [0.0,0.5];
     numRegimes = size(dists);
          
     cycs = zeros((numRuns,numRegimes),dtype='f');
     
     if ( alreadySaved==0 ):
          for j in range(0,numRegimes):
               for i in range(1,numRuns+1):
                    print [dists[j],i];
                    data = GetVACCRun(dists[j],i,useQuad,useLarge);
                    allCycs = [];
                    numCyclicChildren = 0;
                    numChildren = 0;
                    parentIsCyclic = 1;
                    k = size(data,0)-1;
                    numChildren = 0;
                    numCyclicChildren = 0;
                    while ( data[k-1,1] == data[k,1] ):
                         if ( data[k,3]==data[k,23] ):
                              numCyclicChildren = numCyclicChildren+1;
                         numChildren = numChildren+1;
                         k = k-1;

                    if ( numChildren>0 ):
                         cycs[i-1,j] = float(numCyclicChildren)/float(numChildren);

          if ( useQuad ):
               if ( useLarge ):
                    save("../Data/QuadLarge/cycs.dat",cycs,fmt='%5.5f',delimiter=' ');
               else:
                    save("../Data/Quad/cycs.dat",cycs,fmt='%5.5f',delimiter=' ');
          else:
               save("../Data/Hex/cycs.dat",cycs,fmt='%5.5f',delimiter=' ');

     if ( useQuad ):
          if ( useLarge ):
               fits = load("../Data/QuadLarge/fitsQuadLarge.dat");
               cycs = load("../Data/QuadLarge/cycs.dat");
          else:
               fits = load("../Data/Quad/fitsQuad.dat");
               cycs = load("../Data/Quad/cycs.dat");          
     else:
          fits = load("../Data/Hex/fitsHex.dat");
          cycs = load("../Data/Hex/cycs.dat");
               
     print fits;
     print cycs;

     figure(figNo);
     clf();

     markers    = ['k^','bs','gv','ro','c<','mD','y>'];
     lineColors = ['k-','b-','g-','r-','c-','m-','y-'];

     legends = ['d=0.0m','d=0.5m','d=1.0m','d=1.5m','d=2.0m','d=2.5m','d=3.0m'];

     xmin = 0.0;
     xmax = 9.0;
     ymin = 0.0;
     ymax = 0.85;
     x = zeros(2,dtype='f');
     x[0] = xmin;
     x[1] = xmax;
     y = zeros(2,dtype='f');
     for j in range(0,numRegimes):
          m,b = polyfit( fits[0:numRuns,j] , cycs[0:numRuns,j] , 1 );
          y[0] = m*x[0]+b;
          y[1] = m*x[1]+b;
          plot(x,y,lineColors[j],label='_nolegend_',linewidth=2);
     
     for j in range(0,numRegimes):
          plot(fits[0:numRuns,j],cycs[0:numRuns,j],markers[j],label=legends[j]);

     xlim(xmin,xmax);
     ylim(ymin,ymax);
     xlabel('Final target distance (m)');
     ylabel('Fraction of cyclic children');
     
     le = legend(loc='lower right');

     if ( useQuad ):
          if ( useLarge ):
               title('Quadruped (h=4)');
               savefig('../Images/QuadLargeCycs.eps');
          else:
               title('Quadruped (h=0)');
               savefig('../Images/QuadCycs.eps');
     else:
          title('Hexapod (h=0)');
          savefig('../Images/HexCycs.eps');
               
     #show();

def CompareTotalEvalTimes(figNo,alreadySaved,useLarge):

     numRuns = 35;
     #numRuns = 2;
     
     dists = [0.0,0.5,1.0,1.5,2.0,2.5,3.0];
     #dists = [0.0,0.5];
     numRegimes = size(dists);

     ratios = zeros((numRuns,numRegimes),dtype='f');
     
     if ( alreadySaved==0 ):
          for j in range(0,numRegimes):
               for i in range(1,numRuns+1):
                    print [dists[j],i];
                    data = GetVACCRun(dists[j],i,1,useLarge);
                    ratios[i-1,j] = data[-1,3];
          if ( useLarge ):
               save("../Data/QuadLarge/totalEvals.dat",ratios,fmt='%5.5f',delimiter=' ');
          else:
               save("../Data/Quad/totalEvals.dat",ratios,fmt='%5.5f',delimiter=' ');

     if ( useLarge ):
          fits = load("../Data/QuadLarge/fitsQuadLarge.dat");
          ratios = load("../Data/QuadLarge/totalEvals.dat");
     else:
          fits = load("../Data/Quad/fitsQuad.dat");
          ratios = load("../Data/Quad/totalEvals.dat");          

     print fits;
     print ratios;

     figure(figNo);
     clf();

     markers = ['k^','bs','gv','ro','c<','mD','y>'];
     legends = ['d=0.0m','d=0.5m','d=1.0m','d=1.5m','d=2.0m','d=2.5m','d=3.0m'];
     
     for j in range(0,numRegimes):
          plot(fits[0:numRuns,j],ratios[0:numRuns,j]*0.005,markers[j],label=legends[j]);

     xlabel('Final target distance (m)');
     ylabel('Total evaluation time(s)');

     le = legend(loc='lower right');
     
     if ( useLarge ):
          title('Quadruped (h=4)');
          savefig('../Images/QuadLargeTotalEvals.eps');
     else:
          title('Quadruped (h=0)');
          savefig('../Images/QuadTotalEvals.eps');
     
def CompareEvalTimes(figNo,alreadySaved,useLarge):

     numRuns = 35;
     #numRuns = 2;
     
     dists = [0.0,0.5,1.0,1.5,2.0,2.5,3.0];
     #dists = [0.0,0.5];
     numRegimes = size(dists);

     ratios = zeros((numRuns,numRegimes),dtype='f');

     if ( useLarge ):
          maxAllowedTime = 2730;
     else:
          maxAllowedTime = 3630;
     
     if ( alreadySaved==0 ):
          for j in range(0,numRegimes):
               for i in range(1,numRuns+1):
                    print [dists[j],i];
                    data = GetVACCRun(dists[j],i,1,useLarge);
                    totalTimes = data[:,3];
                    actualTimes = data[:,23];
                    timeRatios = [];
                    for k in range(0,size(data,0)):
                         if ( data[k,3]<=maxAllowedTime ):
                              if ( data[k,23]==data[k,3] ):
                                   timeRatios.append(1);
                              else:
                                   timeRatios.append(0);
                    ratios[i-1,j] = mean(timeRatios);
          if ( useLarge ):
               save("../Data/QuadLarge/evalRatios.dat",ratios,fmt='%5.5f',delimiter=' ');
          else:
               save("../Data/Quad/evalRatios.dat",ratios,fmt='%5.5f',delimiter=' ');

     if ( useLarge ):
          fits = load("../Data/QuadLarge/fitsQuadLarge.dat");
          ratios = load("../Data/QuadLarge/evalRatios.dat");
     else:
          fits = load("../Data/Quad/fitsQuad.dat");
          ratios = load("../Data/Quad/evalRatios.dat");          

     print fits;
     print ratios;

     figure(figNo);
     clf();

     markers = ['k^','bs','gv','ro','c<','mD','y>'];
     legends = ['d=0.0m','d=0.5m','d=1.0m','d=1.5m','d=2.0m','d=2.5m','d=3.0m'];
     
     for j in range(0,numRegimes):
          plot(fits[0:numRuns,j],ratios[0:numRuns,j],markers[j],label=legends[j]);

     xlabel('Final target distance (m)');
     ylabel('Evaluation time ratio');

     le = legend(loc='lower right');
     
     if ( useLarge ):
          title('Quadruped (h=4)');
          savefig('../Images/QuadLargeEvalRatios.eps');
     else:
          title('Quadruped (h=0)');
          savefig('../Images/QuadEvalRatios.eps');
          
def CompareMutations(figNo,alreadySaved,useQuad,useLarge):

     numRuns = 35;
     #numRuns = 2;
     
     dists = [0.0,0.5,1.0,1.5,2.0,2.5,3.0];
     #dists = [0.0,0.5];
     numRegimes = size(dists);

     tauRatios = zeros((numRuns,numRegimes),dtype='f');
     weightsRatios = zeros((numRuns,numRegimes),dtype='f');
     omegasRatios = zeros((numRuns,numRegimes),dtype='f');
     sensorWeightsRatios = zeros((numRuns,numRegimes),dtype='f');

     if ( alreadySaved==0 ):

          for j in range(0,numRegimes):
               
               for i in range(1,numRuns+1):

                    print [dists[j],i];
                    
                    data = GetVACCRun(dists[j],i,useQuad,useLarge);

                    means = zeros((4,2),dtype='f');
                    stds = zeros((4,2),dtype='f');
                    
                    mutTaus = data[:,11];
                    mutWeights = data[:,12];
                    mutOmegas = data[:,13];
                    mutSensorWeights = data[:,14];

                    means[0,0] = mean(mutTaus);
                    means[1,0] = mean(mutWeights);
                    means[2,0] = mean(mutOmegas);
                    means[3,0] = mean(mutSensorWeights);

                    taus = [];
                    weights = [];
                    omegas = [];
                    sensorWeights = [];
                    
                    for k in range(0,size(data,0)-1):
                         #if ( (data[k,1]!=data[k+1,1]) & (data[k,4]>2.0) ):
                         if ( data[k,1]!=data[k+1,1] ):
                         #if ( data[k,2]>=1.825 ):
                              taus.append( data[k,11] );
                              weights.append( data[k,12] );
                              omegas.append( data[k,13] );
                              sensorWeights.append( data[k,14] );
                              
                    means[0,1] = mean(taus);
                    means[1,1] = mean(weights);
                    means[2,1] = mean(omegas);
                    means[3,1] = mean(sensorWeights);    

                    tauRatios[i-1,j]           = means[0,1] / means[0,0];
                    weightsRatios[i-1,j]       = means[1,1] / means[1,0];
                    omegasRatios[i-1,j]        = means[2,1] / means[2,0];
                    sensorWeightsRatios[i-1,j] = means[3,1] / means[3,0];

          if ( useQuad ):
               if ( useLarge ):
                    save("../Data/QuadLarge/mutTau.dat",tauRatios,fmt='%5.5f',delimiter=' ');
                    save("../Data/QuadLarge/mutWeights.dat",weightsRatios,fmt='%5.5f',delimiter=' ');
                    save("../Data/QuadLarge/mutOmegas.dat",omegasRatios,fmt='%5.5f',delimiter=' ');
                    save("../Data/QuadLarge/mutSensorWeights.dat",sensorWeightsRatios,fmt='%5.5f',delimiter=' ');
               else:
                    save("../Data/Quad/mutTau.dat",tauRatios,fmt='%5.5f',delimiter=' ');
                    save("../Data/Quad/mutWeights.dat",weightsRatios,fmt='%5.5f',delimiter=' ');
                    save("../Data/Quad/mutOmegas.dat",omegasRatios,fmt='%5.5f',delimiter=' ');
                    save("../Data/Quad/mutSensorWeights.dat",sensorWeightsRatios,fmt='%5.5f',delimiter=' ');
          else:
               save("../Data/Hex/mutTau.dat",tauRatios,fmt='%5.5f',delimiter=' ');
               save("../Data/Hex/mutWeights.dat",weightsRatios,fmt='%5.5f',delimiter=' ');
               save("../Data/Hex/mutOmegas.dat",omegasRatios,fmt='%5.5f',delimiter=' ');
               save("../Data/Hex/mutSensorWeights.dat",sensorWeightsRatios,fmt='%5.5f',delimiter=' ');          

     if ( useQuad ):
          if ( useLarge ):
               mutTau = load("../Data/QuadLarge/mutTau.dat");
               mutWeights = load("../Data/QuadLarge/mutWeights.dat");
               mutOmegas = load("../Data/QuadLarge/mutOmegas.dat");
               mutSensorWeights = load("../Data/QuadLarge/mutSensorWeights.dat");
          else:
               mutTau = load("../Data/Quad/mutTau.dat");
               mutWeights = load("../Data/Quad/mutWeights.dat");
               mutOmegas = load("../Data/Quad/mutOmegas.dat");
               mutSensorWeights = load("../Data/Quad/mutSensorWeights.dat");
     else:
          mutTau = load("../Data/Hex/mutTau.dat");
          mutWeights = load("../Data/Hex/mutWeights.dat");
          mutOmegas = load("../Data/Hex/mutOmegas.dat");
          mutSensorWeights = load("../Data/Hex/mutSensorWeights.dat");
               
     width = 1.0/float(4.0+1.0);
     
     tauMeans = mean(mutTau);
     tauStds = std(mutTau);
     weightsMeans = mean(mutWeights);
     weightsStds = std(mutWeights);
     omegasMeans = mean(mutOmegas);
     omegasStds = std(mutOmegas);
     sensorWeightsMeans = mean(mutSensorWeights);
     sensorWeightsStds = std(mutSensorWeights);
     
     figure(figNo);
     clf();

     SetFontSize(18);

     x = arange(numRegimes);
     
     p1 = bar(x,tauMeans,width,color='0.0',ecolor='0.0',yerr=tauStds);
     p2 = bar(x+width,weightsMeans,width,color='0.2',ecolor='0.2',yerr=weightsStds);
     p3 = bar(x+2*width,omegasMeans,width,color='0.4',ecolor='0.4',yerr=omegasStds);
     p4 = bar(x+3*width,sensorWeightsMeans,width,color='0.6',ecolor='0.6',yerr=sensorWeightsStds);
          
     xlabel('Starting target distance (m)');
     ylabel('Mutation bias');
     xticks(x+2*width, ('d=0.0','d=0.5','d=1.0','d=1.5','d=2.0','d=2.5','d=3.0') );
     xlim(-width,len(x));

     legend( (p1[0],p2[0],p3[0],p4[0]) , (r'$b_{\tau}$',r'$b_{w}$',r'$b_{\theta}$',r'$b_{n}$') , loc='lower left');
     
     if ( useQuad ):
          if ( useLarge ):
               savefig('../Images/QuadLargeMuts.eps');
               title('Quadruped (h=4)');
          else:
               savefig('../Images/QuadMuts.eps');
               title('Quadruped');
     else:
          savefig('../Images/HexMuts.eps');
          title('Hexapod');

     #show();

def SetFontSize(fontSize):

     rc("axes", labelsize=fontSize, titlesize=fontSize);
     rc("xtick", labelsize=fontSize);
     rc("ytick", labelsize=fontSize);
     rc("font", size=fontSize);
     rc("legend", fontsize=fontSize);
     
def CompareRobustnesses(figNo,fitsSaved,useQuad,useLarge):

     numRuns = 35;
     #numRuns = 2;
     
     dists = [0.0,0.5,1.0,1.5,2.0,2.5,3.0];
     #dists = [0.0,0.5];
     numRegimes = size(dists);

     robustnesses = [ [] for i in range(5*numRegimes) ];
     
     if ( fitsSaved==0 ):
        
          means = zeros((5,numRegimes),dtype='f');
          stds = zeros((5,numRegimes),dtype='f');
          nums = zeros((5,numRegimes),dtype='d');
          allNums = zeros((5,numRegimes),dtype='d');
          successes = zeros((5,numRegimes),dtype='f');
          
          for j in range(0,numRegimes):
               for i in range(1,numRuns+1):
                    print [dists[j],i];
                    data = GetVACCRun(dists[j],i,useQuad,useLarge);
                    ln = size(data,0);
                    for k in range(1,ln):
                         if ( data[k-1,4] < data[k,4] ):
                              dist = data[k-1,4];
                              dist = int(floor(dist));
                              robustness = data[k-1,16];
                              if ( dist < 5 ):
                                   if ( robustness > 1 ):
                                        robustnesses[dist*numRegimes + j].append(robustness);
                                        nums[dist,j] = nums[dist,j] + 1;
                                        successes[dist,j] = successes[dist,j]+1;
                                   allNums[dist,j] = allNums[dist,j] + 1;

          for i in range(0,5):
               for j in range(0,numRegimes):
                    if ( nums[i,j] > 0 ):
                         means[i,j] = mean( robustnesses[i*numRegimes+j] );
                         stds[i,j] = std( robustnesses[i*numRegimes+j] );
                         successes[i,j] = successes[i,j] / float(allNums[i,j]);
          
          if ( useQuad ):
               if ( useLarge ):
                    save("../Data/QuadLarge/robustsQuadLarge_means.dat",means,fmt='%5.5f',delimiter=' ');
                    save("../Data/QuadLarge/robustsQuadLarge_stds.dat",stds,fmt='%5.5f',delimiter=' ');
                    save("../Data/QuadLarge/robustsQuadLarge_successes.dat",successes,fmt='%5.5f',delimiter=' ');
                    save("../Data/QuadLarge/robustsQuadLarge_nums.dat",nums,fmt='%d',delimiter=' ');
               else:
                    save("../Data/Quad/robustsQuad_means.dat",means,fmt='%5.5f',delimiter=' ');
                    save("../Data/Quad/robustsQuad_stds.dat",stds,fmt='%5.5f',delimiter=' ');
                    save("../Data/Quad/robustsQuad_successes.dat",successes,fmt='%5.5f',delimiter=' ');
                    save("../Data/Quad/robustsQuad_nums.dat",nums,fmt='%d',delimiter=' ');
          else:
               save("../Data/Hex/robustsHex_means.dat",means,fmt='%5.5f',delimiter=' ');
               save("../Data/Hex/robustsHex_stds.dat",stds,fmt='%5.5f',delimiter=' ');
               save("../Data/Hex/robustsHex_successes.dat",successes,fmt='%5.5f',delimiter=' ');
               save("../Data/Hex/robustsHex_nums.dat",nums,fmt='%d',delimiter=' ');

     else:
          if ( useQuad ):
               if ( useLarge ):
                    means = load("../Data/QuadLarge/robustsQuadLarge_means.dat");
                    stds = load("../Data/QuadLarge/robustsQuadLarge_stds.dat");
               else:
                    means = load("../Data/Quad/robustsQuad_means.dat");
                    stds = load("../Data/Quad/robustsQuad_stds.dat");
          else:
               means = load("../Data/Hex/robustsHex_means.dat");
               stds = load("../Data/Hex/robustsHex_stds.dat");

          print means;

          figure(figNo);
          clf();

          x = arange(0,5);

          for j in range(0,numRegimes):
               errorbar( x+(float(j)/10), means[:,j] , stds[:,j] , fmt=None, color='1.0', ecolor='k', label='_nolegend_');

          markerSize=8;
          plot( x+(float(0)/10) , means[:,0] , 'k^' , markersize=markerSize , label='d=0.0');
          plot( x+(float(1)/10) , means[:,1] , 'bs' , markersize=markerSize , label='d=0.5');
          plot( x+(float(2)/10) , means[:,2] , 'gv' , markersize=markerSize , label='d=1.0');
          plot( x+(float(3)/10) , means[:,3] , 'ro' , markersize=markerSize , label='d=1.5');
          plot( x+(float(4)/10) , means[:,4] , 'c<' , markersize=markerSize , label='d=2.0');
          plot( x+(float(5)/10) , means[:,5] , 'mD' , markersize=markerSize , label='d=2.5');
          plot( x+(float(6)/10) , means[:,6] , 'y>' , markersize=markerSize , label='d=3.0');

          le = legend(loc='lower right');

          xlabel('Successful Target Distance (m)');
          ylabel('Half fitness');

          if ( useQuad ):
               if ( useLarge ):
                    title('Quadruped Large');
                    savefig('../Images/QuadLargeAll.eps');
               else:
                    title('Quadruped');
                    savefig('../Images/QuadAll.eps');
          else:
               title('Hexapod');

          #show();
     
def DrawSensorValues(figNo,runNum):

     labels = ['c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r'];

     f = figure(figNo);
     clf();

     numPanels = 4;

     dists = arange(0,320,int(ceil(320/(numPanels*numPanels))));

     for i in range(numPanels*numPanels,0,-1):
          ax = subplot(numPanels,numPanels,i);
          fileName = "../Code/QuadMovie/Data/";
          fileName = fileName+str(runNum)+"_SensorValues_";
          fileName = fileName+str(dists[i-1])+".dat";
          values = load(fileName);
          x = arange( size(values,0) )*0.005;
          plot( x, values[:,0] , 'k-');
          plot( x, values[:,2] , 'r-');
          plot( x, values[:,4] , 'g-');
          plot( x, -values[:,5] , 'b-');
          ax.set_ylim(-1,1);
          if ( i==(numPanels*numPanels) ):
               xmin, xmax = ax.get_xlim();
               xt = floor(arange(xmin,xmax+0.0001,(xmax-xmin)/3.0));
               xticks(xt);
               xlabel('Time (s)');
               yticks([]);
          elif ( i==1 ):
               ax.set_xlim(xmin,xmax);
               xticks([]);
               ylabel('Sensor values');
          else:
               ax.set_xlim(xmin,xmax);
               xticks([]);
               yticks([]);
          titleStr = '('+str(labels[i-1])+')  d=' + str(float(dists[i-1])/100.0) + 'm';
          title(titleStr,fontsize=10);

     show();
    
def CompareDists(figNo,fitsSaved,useQuad,useLarge):

     #numRuns = 35;
     numRuns = 2;
     
     #dists = [0.0,0.5,1.0,1.5,2.0,2.5,3.0];
     dists = [0.0,0.5];
     
     numRegimes = size(dists);
     
     if ( fitsSaved==0 ):
        
          fits = zeros( (numRuns,numRegimes) , dtype='f');

          for j in range(0,numRegimes):
               for i in range(1,numRuns+1):
               #for i in range(2,2+1):
                    print [dists[j],i];
                    data = GetVACCRun(dists[j],i,useQuad,useLarge);
                    fits[i-1,j] = data[-1,4];

          if ( useQuad ):
               if ( useLarge ):
                    save("../Data/QuadLarge/fitsQuadLarge.dat",fits,fmt='%5.5f',delimiter=' ');
               else:
                    save("../Data/Quad/fitsQuad.dat",fits,fmt='%5.5f',delimiter=' ');

          else:
               save("../Data/Hex/fitsHex.dat",fits,fmt='%5.5f',delimiter=' ');

          print fits;

     else:
          if ( useQuad ):
               if ( useLarge ):
                    fits = load("../Data/QuadLarge/fitsQuadLarge.dat");
               else:
                    fits = load("../Data/QuadLarge/fitsQuad.dat");
          else:
               fits = load("../Data/Hex/fitsHex.dat");

          fits = sort(fits,0);
          fits = fits[ceil(3*numRuns/4):numRuns,:];
          #fits = fits[ceil(9*numRuns/10):numRuns,:];
          print fits;

          print mean(fits);
          print std(fits);
          serrs = std(fits) / sqrt(size(fits,0));
          print serrs;
          
          figure(figNo);
          clf();

          x = arange(numRegimes);
          width = 1.0;
          b1 = bar(x,mean(fits),width=1,yerr=std(fits));

          for i in range(0,numRegimes):
               plot(ones((size(fits,0),1),float)*(i+1) - 0.25,fits[:,i],'k.');

          xticks(x+(width/2), ('d=0.0','d=0.5','d=1.0','d=1.5','d=2.0','d=2.5','d=3.0') );

          xlabel('Initial Target Distance (m)');
          ylabel('Final Target Distance (m)');

     if ( useQuad ):
          if ( useLarge ):
               title('Quadruped Large');
               savefig('../Images/QuadLargeAll.eps');
          else:
               title('Quadruped');
               savefig('../Images/QuadAll.eps');
     else:
          title('Hexapod');

     #show();

def CompareDistsByTime(figNo,useQuad):

     numRuns = 100;
     
     dists = [0.0,0.5,1.0,1.5,2.0,2.5,3.0];
     numRegimes = size(dists);

     p = [];
     
     fits = zeros( (numRuns,numRegimes,18) , dtype='f');
               
     for i in range(0,18):
          if ( useQuad ):
          	fileName = "../Data/Quad/hours_fitsQuad_"+str(i)+".dat";
                fits[:,:,i] = load(fileName);
          else:
               fileName = "../Data/Hex/hours_fitsHex_"+str(i)+".dat";
               fits[:,:,i] = load(fileName);

     fits = sort(fits,0);
     fits = fits[70:100,:];
     
     means = mean(fits,0);
     stds = std(fits,0);
     serrs = std(fits,0) / sqrt(30);
     
     f = figure(figNo);
     clf;
     SetFontSize(18);
     
     x = arange(0,18);

     for j in range(0,numRegimes):
          errorbar( x+(float(j)/7), means[j,:] , serrs[j,:] , fmt=None, color='1.0', ecolor='k', label='_nolegend_');

     for j in range(0,18+1):
          plot([j,j],[-0.1,4.5], c='0.5');
                    
     markerSize=12;
     plot( x+(float(0)/7) , means[0,:] , '^' , c='0.4', markersize=markerSize , label='d=0.0');
     plot( x+(float(1)/7) , means[1,:] , 's' , c='0.5', markersize=markerSize , label='d=0.5');
     plot( x+(float(2)/7) , means[2,:] , 'v' , c='0.6', markersize=markerSize , label='d=1.0');
     plot( x+(float(3)/7) , means[3,:] , 'o' , c='0.7', markersize=markerSize , label='d=1.5');
     plot( x+(float(4)/7) , means[4,:] , '<' , c='0.8', markersize=markerSize , label='d=2.0');
     plot( x+(float(5)/7) , means[5,:] , 'D' , c='0.9', markersize=markerSize , label='d=2.5');
     plot( x+(float(6)/7) , means[6,:] , '>' , c='1.0', markersize=markerSize , label='d=3.0');

     le = legend(loc='lower right');

     plot( x+(float(0)/7) , means[0,:] , '^' , c='0.4', markersize=markerSize , label='d=0.0');
     plot( x+(float(1)/7) , means[1,:] , 's' , c='0.5', markersize=markerSize , label='d=0.5');
     plot( x+(float(2)/7) , means[2,:] , 'v' , c='0.6', markersize=markerSize , label='d=1.0');
     plot( x+(float(3)/7) , means[3,:] , 'o' , c='0.7', markersize=markerSize , label='d=1.5');
     plot( x+(float(4)/7) , means[4,:] , '<' , c='0.8', markersize=markerSize , label='d=2.0');
     plot( x+(float(5)/7) , means[5,:] , 'D' , c='0.9', markersize=markerSize , label='d=2.5');
     plot( x+(float(6)/7) , means[6,:] , '>' , c='1.0', markersize=markerSize , label='d=3.0');

     ylim(-0.1,4.5);
     xlim(-0.1,18);
     
     f.subplots_adjust(left=0.03, right=0.99, top=0.92)
     xlabel('Hours since experiment start');
     ylabel('Final target distance (m)');

     if ( useQuad ):
	title('Quadruped');
     else:
          title('Hexapod');

     show();

def GetVACCRun(distIndex,runNum,useQuad,useLarge):

     if ( useQuad ):
          if ( useLarge ):
               fileName = "../Data/QuadLarge" + str(distIndex);
          else:
               fileName = "../Data/QuadCut" + str(distIndex);
     else:
          fileName = "../Data/HexNarrow" + str(distIndex);

     fileName = fileName + "/Data/runData_" + str(runNum) + ".dat";

     data = load(fileName);
     return data;

def PlotRun(figNo,fileName):

     data = load(fileName);

     bests = data[:,1];
     currs = data[:,2];
     times = data[:,3];
     dists = data[:,4];
     hours = data[:,15];

     lines = range(0,31,2);
     lins = [];
     for i in range(len(lines)):
          lins.append(float(lines[i])/10.0);
     lines = lins;
     
     ln = size(data,0);

     f = figure(figNo);
     f.clf();

     # ----------------- Plot improvement by wallclock time
     ax = subplot(121);
     distIndex = 0;
     i = 0;
     while ( distIndex<len(lines)):
          if ( (data[i,4]<data[i+1,4]) & (data[i,4]==lines[distIndex]) ):
               currHour = data[i,15];
               currDist = data[i,4];
               
               plot([0,currHour],[currDist,currDist],'k-');
               plot([currHour,currHour],[0,currDist],'k-');

               distIndex = distIndex + 1;
          i=i+1;
     plot(hours,dists,'k-',linewidth=2);
     ax.set_xlim(0,18);
     ax.set_ylim(0,3.2);
     xlabel('Time (h)');
     ylabel('Target distance (m)');
     
     # ----------------- Plot improvement by mutation distance
     ax = subplot(122);
     x = [0];
     y = [0];
     i = 0;
     numMuts = 0;
     distIndex = 0.01;
     while ( distIndex<data[-1,4] ):
          if ( data[i,1]!=data[i+1,1] ):
               numMuts = numMuts + 1;
          if ( data[i,4]<data[i+1,4] ):
               x.append(numMuts);
               y.append(distIndex);
               distIndex = distIndex + 0.01;
               numMuts = 0;
          i=i+1;

     for i in range(1,len(x)):
          x[i] = x[i-1] + x[i];
          
     plot(x,y,'k-',linewidth=2);

     labels = ['c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r'];
     for i in range(len(lines)):
          currX = x[int(lines[i]*100.0)];
          currY = y[int(lines[i]*100.0)];
          plot([0,currX],[currY,currY],'k-');
          plot([currX,currX],[0,currY],'k-');
          if ( i==0 ):
               text(currX,currY,labels[i]);
          else:
               text(currX-50,currY,labels[i]);

     ax.set_ylim(0,3.2);

     xlabel('Number of mutations');

     show();
        
def PlotLocalRun(figNo,runNum):

    fileName = "../Code/Quad/Data/runData_" + str(runNum);
    fileName = fileName + ".dat";
    PlotRun(figNo,fileName);

def PlotVACCRun(figNo,dist,runNum,useQuad):

    if ( useQuad ):
        fileName = "../Data/QuadCut"+str(dist)+"/Data/runData_" + str(runNum);
    else:
        fileName = "../Data/HexCut"+str(dist)+"/Data/runData_" + str(runNum);
        
    fileName = fileName + ".dat";
    
    PlotRun(figNo,fileName);


# --------------------- Main function -----------------------------

PlotLocalRun(1,14); #Fig. 3a,b
DrawSensorValues(2,14); #Fig. 3c-r

CompareDistsByTime(3,1);   #Fig. 4a
CompareDistsByTime(4,0);  # Fig. 4b
