# -*- coding: utf-8 -*-
"""Untitled

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oqR89XuhVn0Ws_sdrCXUAomEH92pLuxw
"""

!mkdir outputs
!mkdir outputs/snapshot

!pip install deap
!pip install svgwrite

import poppySimRobot as psr
import numpy as np
import matplotlib.pyplot as plt
import sketch_pix2seq_sampling as sketch
import copy 
import array
import random
import numpy
import pickle
from PIL import Image
from cv2 import *

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import matplotlib.pyplot as plt
from random import randint

class CTRNN:
    def sigmoid(self,s):
        return 1/(1+np.exp(-s))

    def __init__(self,size=2,step_size=0.1):
        self .size = size
        self.step_size = step_size
        self.taus = np.random.rand(self .size)
        self.biases = np.random.rand(self.size)
        self.gains = np.random.rand(self.size)
        self.weights = np.random.rand(self.size,self.size)
        self.initial_state = np.random.rand(self.size)
        self.states = np.copy(self.initial_state)
        self.outputs = self.sigmoid(self.states)
    def euler_step(self,external_inputs):
        external_inputs = np.asarray(external_inputs)
        total_inputs = self.weights.dot(self.outputs)
        self.states += self.step_size*self.taus*(total_inputs - self.states) 
        self.outputs = self.sigmoid(self.gains*(self.states+self.biases))
        return self.outputs
    def inverse_sigmoid(self,o):
        inverse_sig = np.log(o/(1-o))
        return inverse_sig

CTRNN_Model = CTRNN(3,0.5)

def lossFunction(target, predict):
  compare = target == predict
  score = 0
  return np.sum(compare)
def load_image_png(png_path):
  image = Image.open(png_path).convert('L')
  image = np.array(image, dtype=np.float32)
  return image

low_range = -30
high_range = 30
def generateR():
  return random.uniform(low_range, high_range)

number_population = 150
#number_individual = image_size_target*image_size_target + image_size_target*3 #W, Bias, Taus, Gains
generations = 30
_cxpb=0.5
_mutpb=0.2

steps_for_image = sketch.sampling_conditional_Modified("./","./","./outputs/snapshot")

print(steps_for_image.shape)

#For drawing
x_min = 0
x_max = 1
y_min = 0
y_max = 10

poppy = psr.PoppySimMath()

CTRNN_Model = CTRNN(3,0.5)
outputs = []
for i in range(len(steps_for_image)):
  val = CTRNN_Model.euler_step(steps_for_image[i])
  val = psr.calculateAngleScale(val,x_min,x_max,y_min,y_max)
  mov_brazo = poppy.moveLeftArm(psr.getRadAngles(val))
  outputs.append(mov_brazo)
outputs = np.asarray(outputs)
x_arrow,z_arrow = psr.getArrow(outputs)
image = psr.drawImage(48,x_arrow,z_arrow)
target = load_image_png("./200.png")
print(lossFunction(target, image))
cv2.imwrite('houghlines3.jpg',image)

print(CTRNN_Model.weights.shape)
print(CTRNN_Model.biases.shape)
print(CTRNN_Model.taus.shape)
print(CTRNN_Model.gains.shape)

number_individual = CTRNN_Model.size*CTRNN_Model.size + CTRNN_Model.size*3

modelo = CTRNN(3,0.1)
creator.create("FitnessMax", base.Fitness, weights=(1.0,))#Maximizar la función
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_bool", generateR)#Método de generación

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, number_individual)#Generador de individuos
toolbox.register("population", tools.initRepeat, list, toolbox.individual)#Generador de población
#Función de mutación
def mutUniformFloat(individual, indpb):
  size = len(individual)
  for i in range(size):
      if random.random() < indpb:
          value = generateR()
          individual[i] = value
  return individual,
  
#Función de fitness
def evaluateIndividual(individual):
    global modelo
    x_min = 0
    x_max = 1
    y_min = 0
    y_max = 5
    updateWeights(modelo,individual)

    poppy = psr.PoppySimMath()
    outputs = []
    for i in range(len(steps_for_image)):
      val = modelo.euler_step(steps_for_image[i])
      val = psr.calculateAngleScale(val,x_min,x_max,y_min,y_max)
      mov_brazo = poppy.moveLeftArm(psr.getRadAngles(val))
      outputs.append(mov_brazo)
    outputs = np.asarray(outputs)
    x_arrow,z_arrow = psr.getArrow(outputs)
    image = psr.drawImage(48,x_arrow,z_arrow)
    target = load_image_png("./200.png")
    score = lossFunction(target, image)  
    return score,
def updateWeights(model,individual):
  full_size = model.size
  limit = full_size*full_size
  states = np.copy(model.initial_state)
  W = individual[:limit].reshape(full_size,full_size)
  
  newLimit = limit+full_size
  Biases = individual[limit:newLimit].reshape(full_size,)
  
  limit = newLimit
  newLimit = limit+full_size
  
  Taus = individual[limit:newLimit].reshape(full_size,)
  
  limit = newLimit
  newLimit = limit+full_size  
  
  Gains = individual[limit:newLimit].reshape(full_size,)
  
  model.states = states
  model.outputs = model.sigmoid(model.states)
  model.weights = W
  model.biases = Biases
  model.taus = Taus
  model.gain = Gains

#Acciones a realizar
toolbox.register("evaluate", evaluateIndividual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutUniformFloat,indpb=0.5)
toolbox.register("select", tools.selTournament,tournsize=3  )
def varAnd(population, toolbox, cxpb, mutpb):
    offspring = [toolbox.clone(ind) for ind in population]

    # Apply crossover and mutation on the offspring
    for i in range(1, len(offspring), 2):
        if random.random() < cxpb:
            offspring[i - 1], offspring[i] = toolbox.mate(offspring[i - 1],
                                                          offspring[i])
            del offspring[i - 1].fitness.values, offspring[i].fitness.values

    for i in range(len(offspring)):
        if random.random() < mutpb:
            offspring[i], = toolbox.mutate(offspring[i])
            del offspring[i].fitness.values

    return offspring
  

def eaSimple(population, toolbox, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=__debug__):
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))

        # Vary the pool of individuals
        offspring = varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook

def executeAE():
    pop = toolbox.population(n=number_population)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    stats.register("median", numpy.median)
    
    
    pop, log = eaSimple(pop, toolbox, cxpb=_cxpb, mutpb=_mutpb, ngen=generations, 
                                   stats=stats, verbose=True)
    
    
    return pop, log

pop, log = executeAE()

HOF = 0
max_success = 0
for individual in pop:
  evaluate = evaluateIndividual(individual)
  if evaluate[0] > max_success:
    max_success = evaluate[0]
    HOF = individual
global modelo
x_min = 0
x_max = 1
y_min = 0
y_max = 10
updateWeights(modelo,HOF)

np.save("./HOF.npy", HOF)
poppy = psr.PoppySimMath()
outputs = []
for i in range(len(steps_for_image)):
  val = modelo.euler_step(steps_for_image[i])
  val = psr.calculateAngleScale(val,x_min,x_max,y_min,y_max)
  mov_brazo = poppy.moveLeftArm(psr.getRadAngles(val))
  outputs.append(mov_brazo)
outputs = np.asarray(outputs)
x_arrow,z_arrow = psr.getArrow(outputs)
image = psr.drawImage(48,x_arrow,z_arrow)
cv2.imwrite("Mejor_Resultado.png",image)
target = load_image_png("./200.png")
score = lossFunction(target, image)
print("Best Score: ")  
print(score)

