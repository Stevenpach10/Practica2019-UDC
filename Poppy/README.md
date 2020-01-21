# Pypot library modified
The pypot library is responsible for
the control of robots used in dynamixel engines. The Integrated Engineering Group of the University of the Coruña has modified that library for their optimization using V-REP simulator.

### Documentation
The original documentation for the library is available at [documentation pypot](http://poppy-project.github.io/pypot/). There also in the file [./Manual_uso_Poppy.docx](Manual_uso_Poppy.docx) you can find a user guide of Poppy robot as well as use examples, instalation and  avaible media.

### Instalation
1. Uninstall the original pypot library if you have installed it before.
```
	pip uninstall pypot
```
2. Go to the directory [pypot/pypot_sensors-sensors_from_config](./pypot/pypot_sensors-sensors_from_config)
```
	cd ./pypot/pypot_sensors-sensors_from_config
```
3. Execute the file [setup.py](./pypot/pypot_sensors-sensors_from_config/setup.py) for the installation
```
	python setup.py install
```
4. Now go to the directory [/pypot/FilesToCopy](./pypot/FilesToCopy) and we going to copy and replace all folders where the python site-packages are installed. An example of root is:
*/home/user/anaconda2/lib/python2.7/site-packages*.
This step is necessary only if the modified library present any error.
```
cd ..
cd ./FileToCopy
sudo cp -r ./  /home/user/anaconda2/lib/python2.7/site-packages
```

In the folder [pypot/pypot_sensors-sensors_from_config/samples/notebooks](./pypot/pypot_sensors-sensors_from_config/samples/notebooks) you will find some useful examples for check if it is working correctly. For this step is necessary have installed V-REP simulator [Using sensors added to V-REP scene.ipynb](./pypot/pypot_sensors-sensors_from_config/samples/notebooks/sensors_usage/Using_sensors_added_to_V-REP_scene.ipynb)
## Credits
1. The library Pypot code is available at [Pypot](https://github.com/poppy-project/pypot)
2. The Integrated Engineering Group of the University of the Coruña for this great contribution.