#Based on the code of https://github.com/gsurma/cartpole/blob/master/cartpole.py
#pip install Keras
#pip install gym
import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


#from scores.score_logger import ScoreLogger

PROBLEM_ENVIRONMENT = "CartPole-v1"

GAMMA = 0.95
LEARNING_RATE = 0.001

MEMORY_SIZE = 1000000
BATCH_SIZE = 20

EXPLORATION_MAX = 1.0
EXPLORATION_MIN = 0.01
EXPLORATION_DECAY = 0.995
MODEL_Q_HIDDEN_UNITS = 24

"""
ModelQ replaces the Q table for estimating all q values for next state s(t+1)
"""
class ModelQ:

    """
    ModelQ builder
    @param stateDimensionality, number of components for a problem state, observed by the agent
    @param numberPossibleActions, number of possible actions for the agent
    """
    def __init__(self, stateDimensionality, numberPossibleActions):
        #the exploration rate defines the ammount of trust for the Q model
        self.explorationRate = EXPLORATION_MAX
        #number of possible actions for the agent
        self.numberPossibleActions = numberPossibleActions
        #Agent memory of quartets <s(t), a(t), r(t), s(t+1), done> appending if its the final quartet of an episode
        #For all the episodes lived by the agent
        self.experience = deque(maxlen = MEMORY_SIZE)
        #A fully connected model is created for estimating q values for all actions
        self.model = Sequential()
        #One input unit per state dimension
        #MODEL_Q_HIDDEN_UNITS output units for the first layer
        self.model.add(Dense(MODEL_Q_HIDDEN_UNITS, input_shape = (stateDimensionality,), activation = "relu"))
        #For a sequential Keras model is not necessary to specify the input dimensionality anymore
        #MODEL_Q_HIDDEN_UNITS for another fully connected layer
        self.model.add(Dense(MODEL_Q_HIDDEN_UNITS, activation = "relu"))
        #Output layer has one output unit per possible action
        self.model.add(Dense(self.numberPossibleActions, activation="linear"))
        self.model.compile(loss = "mse", optimizer = Adam(lr = LEARNING_RATE))

    """
    Queues a cuartet into the agent memory <s(t), a(t), r(t), s(t+1), done>
    @param state, s(t)
    @param action, a(t)
    @param reward, r(t)
    @param nextState, s(t+1)
    @param done, indicate if its the final state in an episode
    """
    def remember(self, state, action, reward, nextState, done):
        self.experience.append((state, action, reward, nextState, done))
    """
    Given a state s(t), outputs an action
    @param state, s(t)
    @return action a(t)
    """
    def act(self, state):
        #a higher exploration rate favors random actions
        if np.random.rand() < self.explorationRate:
            return random.randrange(self.numberPossibleActions)
        #returns a list of lists of q values (only one first list is of interest)
        qValues = self.model.predict(state)
        #picks the action with the highest q value
        return np.argmax(qValues[0])

    """
    Updates modelQ parameters from experience
    """
    def learnFromExperience(self):
        #if the experience is not large enough to pick a batch of BATCH_SIZE, do nothing
        if len(self.experience) < BATCH_SIZE:
            return
        #takes a random batch from agent's experience
        batch = random.sample(self.experience, BATCH_SIZE)
        #for each cuartet in the experience...
        for state, action, reward, nextState, terminal in batch:
            #if the state is final for an episode, just use the reward
            qUpdate = reward
            if not terminal:
                #Q(s(t), a(t)) = r(t) + GAMMA(max a Q(s(t+1))) equation (1)
                qUpdate = (reward + GAMMA * np.amax(self.model.predict(nextState)[0]))
            #the rest of qValues for actions with lower Q values are predicted by the model
            qValues = self.model.predict(state)
            #the action with the best Q value is updated given the equation (1)
            qValues[0][action] = qUpdate
            #Online modelQ training
            self.model.fit(state, qValues, verbose = 0)
        #Linear exploration rate decrease
        self.explorationRate *= EXPLORATION_DECAY
        self.explorationRate = max(EXPLORATION_MIN, self.explorationRate)

"""
Start cartpole learning and simulation
"""
def startCartPoleTrainingAndSimulation():
    #Create cart pole environment
    environment = gym.make(PROBLEM_ENVIRONMENT)
    #Number of state components
    stateDimensions = environment.observation_space.shape[0]
    #Number of possible actions
    numberPossibleActions = environment.action_space.n
    #Create the Q model
    modelQ = ModelQ(stateDimensions, numberPossibleActions)
    #episode number
    episodeNumber = 0
    while True:
        episodeNumber += 1
        #when a new episode starts, reset the state and step t
        state = environment.reset()
        state = np.reshape(state, [1, stateDimensions])
        stepT = 0
        while True:
            stepT += 1
            #render the current simulation step
            environment.render()
            #calculate the agent action
            action = modelQ.act(state)
            #get the next state s(t+1), reward r(t), and if its the final state (the agent failed)
            nextState, reward, terminal, info = environment.step(action)
            #if terminal is true, the agent has failed and the episode has ended
            reward = reward if not terminal else -reward
            #reshape nextState
            nextState = np.reshape(nextState, [1, stateDimensions])
            #add the quartet to the agent experience
            modelQ.remember(state, action, reward, nextState, terminal)
            #state update
            state = nextState
            if terminal:
                #the overall score is given by the time elapsed in the episode
                print("Run: " + str(episodeNumber) + ", exploration: " + str(modelQ.explorationRate) + ", score: " + str(stepT))
                break
            modelQ.learnFromExperience()


if __name__ == "__main__":
    startCartPoleTrainingAndSimulation()