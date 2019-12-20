#Biblioteca de pypot modificada.
La biblioteca Pypot es la encargada del control de robots basados en motores dynamixel. El Grupo Integrado de Ingeniería de la Universidade Da Coruña ha modificado la biblioteca para optimizar su uso en el simulador V-REP.

### Documentación 
La documentación original de la biblioteca está disponbile en [pypot documentación](http://poppy-project.github.io/pypot/). También en el documento [./Manual_uso_Poppy.docx](Manual_uso_Poppy.docx) encontrará una guía del uso del robot Poppy así como diversos ejemplos, instalación y medios de comunicación disponibles.   

### Instalación
1. Desinstalar la biblioteca original de Pypot en caso de tenerla instalada.
```
	pip uninstall pypot
```
2. Ir al direcctorio [pypot/pypot_sensors-sensors_from_config](./pypot/pypot_sensors-sensors_from_config)
```
	cd ./pypot/pypot_sensors-sensors_from_config
```
3. Ejecutar el archivo [setup.py](/pypot/pypot_sensors-sensors_from_config/setup.py)
```
	python setup.py install
```
4. Ahora vamos al directorio [/pypot/FilesToCopy](./pypot/FilesToCopy) y copiamos todas las carpetas en la dirección donde se encuentre instalado el site-packages de python y REEMPLAZAMOS. Un ejemplo de la ruta de instalación sería
*/home/user/anaconda2/lib/python2.7/site-packages* . Este paso es necesario solo si la biblioteca modificada presenta algun problema.
```
cd ..
cd ./FileToCopy
sudo cp -r ./  /home/user/anaconda2/lib/python2.7/site-packages
```

En la carpeta [pypot/pypot_sensors-sensors_from_config/samples/notebooks](./pypot/pypot_sensors-sensors_from_config/samples/notebooks) podrá encontrar varios ejemplos de uso por ejemplo para comprobar que este funcionando adecuadamente. Para este paso es necesario tener instalado el V-REP. [Using sensors added to V-REP scene.ipynb](./pypot/pypot_sensors-sensors_from_config/samples/notebooks/sensor_usage/Using sensors added to V-REP scene.ipynb)
### Creditos
1. El código de la biblioteca de Pypot esta disponible en [Pypot](https://github.com/poppy-project/pypot)
2. Grupo Integrado de Ingeniería por el aporte a la biblioteca.