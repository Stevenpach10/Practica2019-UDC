CODE, DATA AND VISUALIZATION FOR
-------------------------------------------------------------------------------
"Behavior Chaining: Incremental Behavior Integration for Evolutionary Robotics"
J. Bongard
Presented at Artificial Life XI, Winchester, UK, 2008



CODE (For Linux and OS/X platforms only)
-------------------------------------------------------------------------------
1. Open a console window and navigate to Code/Quad/EE
2. Enter './makeODE' to compile the hill climber.
3. Open a second window and navigate to Code/Quad/Target
4. Enter './makeODE' to compile the simulation framework.
4a.   Make sure Open Dynamics Engine v0.9 is installed off your $HOME directory
5. In the EE window type './GA_Camera -r 1 -h 0 -m 5'
5a.   This will initiate a run with random seed 1, no hidden neurons in the
      CTRNN, and a mutation rate of 5. (The settings used in the paper.)
6. In the Target window type './MorphEngine -r 1'
6a.   This will start the simulation, which accepts controllers from
      GA_Camera, and sends back sensor data.
7. The resulting data files are stored in Code/Quad/Data.
8. The same experiments can be run with the hexapod robot by replacing
      'Quad' in the above instructions with 'Hex'.



DATA
-------------------------------------------------------------------------------
The raw data used to generate figures 3 and 4 in the paper are stored
in Data/.



VISUALIZATION
-------------------------------------------------------------------------------
1. To re-create figures 3 and 4 from the raw data, open a window and navigate
to Python/.
2. At the command prompt, type 'python Draw_Figures.py'.
