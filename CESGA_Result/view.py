import numpy as np
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from scipy.sparse import csr_matrix
import copy 
import array
import random
import numpy
import pickle
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

step_size = 1
coordinates = 2
image_size = 5
pixel_to_draw = 5
low_range = -10.0
high_range = 10.0
duration = 25


def encode(data):
  encoded = to_categorical(data, image_size)
  return encoded

def decode(datum):
    return np.argmax(datum)

def decode_data(encode_data):
  data_decode = []
  for element in encode_data:
    data_decode = np.append(data_decode, [decode(element[0]), decode(element[1])])
  return data_decode.reshape((len(encode_data), coordinates))

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    epsilon = 0.000001
    return e_x / (e_x.sum(axis=0)+ epsilon) # only difference


class CTRNN:
    def __init__(self,size=2,step_size=0.1):
        self.size = size
        self.step_size = step_size
        self.taus = np.ones((1, size))
        self.biases = np.ones((1, size))
        self.gains = np.ones((1, size))
        self.weights = csr_matrix(np.random.rand(size,size))
        self.initial_state = np.random.rand(2, size)
        self.states = np.copy(self.initial_state)
        self.outputs = softmax(self.states)
    def euler_step(self,external_inputs):
        #total_inputs = np.transpose(external_inputs[0]) + self.weights.dot(np.transpose(self.outputs))
        total_inputs = self.weights.dot(np.transpose(self.outputs))
        x = self.step_size*self.taus* (np.transpose(total_inputs) - self.states)
        self.states += x
        self.outputs = softmax(self.gains*(self.states+self.biases))
    def sigmoid(self,s):
        return 1/(1+np.exp(-s))

    def inverse_sigmoid(self,o):
        inverse_sig = np.log(o/(1-o))
        return inverse_sig

def lossFunction(target, predict):
  #predict = predict.reshape((predict.shape[0]*predict.shape[1]))
  compare = target == predict
  score = 0
  for i in range(len(compare)):
    plus = 0
    for j in range(i+1):
      if(compare[j][0] and compare[j][1]):
        plus += 1
    score = score + plus
  return score

def penality(last_point, actual_point):
  for i in range(-1,2):
    for j in range(-1, 2):
      if(i != 0 or j != 0):
        if(actual_point[0] + i >= 0 and actual_point[0] + i < image_size):
          if(actual_point[1] + j >= 0 and actual_point[1] + j < image_size):
            if(last_point[0] == actual_point[0] + i and last_point[1] == actual_point[1] + j ):
              return 0
  return -1


low_range = -15.0
high_range = 15.0


def generateR():
  return random.uniform(low_range, high_range)

number_population = 350
number_individual = image_size*image_size + image_size*3 #W, Bias, Taus, Gains
generations = 1200
_cxpb=0.7
_mutpb=0.2

Y = np.array([[1,0],[1,1],[1,2],[1,3],[1,4]])
X = np.array([[0,0]])
X = encode(X)

import matplotlib.pyplot as plt
from random import randint

def getImage(size,image):
  img = np.zeros((size,size))
  img.fill(255)
  for x in image:
    img[int(x[0]), int(x[1])] = 0
  return img

def getResultsFromModel(image, save=False,name="Image"):
  plt.imshow(image.squeeze(),cmap='gray', vmin=0, vmax=255)
  if save:
    plt.savefig(name)
  plt.show()

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_bool", generateR)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, number_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
def mutUniformFloat(individual, indpb):
  size = len(individual)
  for i in range(size):
      if random.random() < indpb:
          value = generateR()
          individual[i] = value
  return individual,
  
def evaluateIndividual(individual):
    output = []
    X = np.array([[0,0]])
    X = encode(X)
    updateWeights(individual)
    for _ in range(pixel_to_draw):
      CTRNN_MODEL.euler_step(X)
      output.append([CTRNN_MODEL.outputs[i] for i in range(2)])
      X = decode_data(CTRNN_MODEL.outputs)
    output = np.asarray(output)  
    output = decode_data(output)
    score = lossFunction(Y,output)
    #for i in range(1, len(output)):
    #  score += penality(output[i-1],output[i])
    return score,
def updateWeights(individual):
  #print(individual)
  limit = image_size*image_size
  CTRNN_MODEL.states = np.copy(CTRNN_MODEL.initial_state)
  CTRNN_MODEL.outputs = softmax(CTRNN_MODEL.states)
  CTRNN_MODEL.weights = individual[:limit].reshape(image_size,image_size)
  
  newLimit = limit+image_size
  
  CTRNN_MODEL.biases = individual[limit:newLimit].reshape(1,image_size)
  
  limit = newLimit
  newLimit = limit+image_size
  CTRNN_MODEL.taus = individual[limit:newLimit].reshape(1,image_size)

  limit = newLimit
  newLimit = limit+image_size  
  CTRNN_MODEL.gain = individual[limit:newLimit].reshape(1,image_size)

#Acciones a realizar
toolbox.register("evaluate", evaluateIndividual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutUniformFloat,indpb=0.5)
toolbox.register("select", tools.selTournament, tournsize=3)

def executeAE():
    pop = toolbox.population(n=number_population)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    stats.register("median", numpy.median)
    
    
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=_cxpb, mutpb=_mutpb, ngen=generations, 
                                   stats=stats, verbose=False)
    
    
    return pop, log

with open('filename_seed_8.pickle', 'rb') as handle:
    dic_load = pickle.load(handle)
    print(dic_load["BEST_SCORE"])

def plotFitness(avg, mini, maxi, gene, median):
  
  fig, ax1 = plt.subplots()
  line1 = ax1.plot(gene, median, "b-", label="Median Success")
  ax1.set_xlabel("Generation")
  ax1.set_ylabel("Median Success", color="b")
  for tl in ax1.get_yticklabels():
      tl.set_color("b")
      
  ax2 = ax1.twinx()
  line2 = ax2.plot(gene, avg, "r-", label="Average Success")
  ax2.set_ylabel("Average Success", color="r")
  for tl in ax2.get_yticklabels():
      tl.set_color("r")

  plt.show()


MODEL = []
AVG = []
MIN = []
MAX = []
GENE = []
MEDIAN = []
CTRNN_MODEL = []
directory = './filename_seed_8.pickle'
with open(directory, 'rb') as handle:
    dic_load = pickle.load(handle)
    MIN = dic_load["MIN"]
    AVG = dic_load["AVG"]
    MAX = dic_load["MAX"]
    GENE = dic_load["GENE"]
    MEDIAN = dic_load["MEDIAN"]
    CTRNN_MODEL = dic_load["MODEL"]

plotFitness(AVG, MIN, MAX, GENE, MEDIAN)

def printImage(output,save=False,name="Image"):
 
  plt.plot(np.arange(0,duration,1),output[:,0,0],'go-',label='Pixel 0',c='g')
  plt.plot(np.arange(0,duration,1),output[:,0,1],'go-',label='Pixel 1',c='r')
  plt.plot(np.arange(0,duration,1),output[:,0,2],'go-',label='Pixel 2',c='c')
  plt.plot(np.arange(0,duration,1),output[:,0,3],'go-',label='Pixel 3',c='m')
  plt.plot(np.arange(0,duration,1),output[:,0,4],'go-',label='Pixel 4',c='b')
  plt.legend()
  plt.xlabel('Time')
  plt.ylabel('Neuron output for axis Y')
  if save:
    plt.savefig(name + "_Axis_Y")
  plt.show()
  plt.plot(np.arange(0,duration,1),output[:,1,0],'go-',label='Pixel 0',c='g')
  plt.plot(np.arange(0,duration,1),output[:,1,1],'go-',label='Pixel 1',c='r')
  plt.plot(np.arange(0,duration,1),output[:,1,2],'go-',label='Pixel 2',c='c')
  plt.plot(np.arange(0,duration,1),output[:,1,3],'go-',label='Pixel 3',c='m')
  plt.plot(np.arange(0,duration,1),output[:,1,4],'go-',label='Pixel 4',c='b')
  plt.legend()
  plt.xlabel('Time')
  plt.ylabel('Neuron output for axis X')
  if save:
    plt.savefig(name + "_Axis_X")
  plt.show()
  
X = np.array([[0,0]])
X = encode(X)
output = []
for _ in range(duration):
  CTRNN_MODEL.euler_step(X)
  output.append([CTRNN_MODEL.outputs[i] for i in range(2)])
  X = decode_data(CTRNN_MODEL.outputs)
output = np.asarray(output)

printImage(output,False,"Image_Cruz")

output = decode_data(output)
image = getImage(image_size,output[:5])
score = lossFunction(Y,output[:5])
getResultsFromModel(image,False,"Image_Cruz")
print("Score : "+str(score))
print(output[:5])
