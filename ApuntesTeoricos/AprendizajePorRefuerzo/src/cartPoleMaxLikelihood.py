#Based on http://doktormike.github.io/blog/A-gentle-introduction-to-reinforcement-learning-or-what-to-do-when-you-dont-know-what-to-do/

#pip install gym
#Only numpy, math and gym are needed
import numpy as np
import math
import gym

#Some model hyperparameters
PROBLEM_ENVIRONMENT = "CartPole-v1"
MAX_EPISODES = 5000
BATCH_SIZE = 20
LEARNING_RATE = 2



"""
Sigmoid function evaluation
@param x, sigmoid function input
@return sigmoid(x)
"""
def getSigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

"""
Probability density function based on the sigmoid, for doing action a = 1 (right)
@param omegaParameters, model parameters
@param state, set of agent observations 
"""
def getProbability(omegaParameters, state):
    #vdot calculates the dot product of two vectors
    return getSigmoid(np.vdot(omegaParameters, state))

"""
Calculate the weight rewards using a decay of the form r(t)/(1+gamma)**t
A higher weight for the first action, longer episodes have higher weights
@param rewardsEpisode, the rewards received over an episode
@return returns the weighted rewards for the episode
"""
def getWeightedRewards(rewardsEpisode):
    #gamma defines the decay
    gamma = 1 - 0.99
    #Return an array of zeros with the same shape and type as a given array.
    weightedRewardsEpisode = np.zeros_like(rewardsEpisode)
    for t in range(len(rewardsEpisode)):
        #net present value calculation is used for a decaying weight, starting from the number of steps
        weightedRewardsEpisode[t] = np.npv(gamma, rewardsEpisode[t:len(rewardsEpisode)])
    #normalize weights
    weightedRewardsEpisode -= np.mean(weightedRewardsEpisode)
    weightedRewardsEpisode /= np.std(weightedRewardsEpisode)
    return weightedRewardsEpisode

"""
Calculates the gradient of the loss function
@param action, a(t) to evaluate
@param probability, p(s(t)|omega)
@param dr, QUEEEEE
@param state, s(t)
@return gradient loss
"""
def getGradientLoss(action, probability, dr, state):
    return np.reshape(dr * ((1 - np.array(action)) * probability - action * (1 - np.array(probability))), [len(action), 1]) * state

"""
Train and run the model
"""
def trainAndRunModel():
    #total reward
    rewardSum = 0
    environment = gym.make(PROBLEM_ENVIRONMENT)
    #Extract the state from the environment
    state = environment.reset()
    #Omega vector of parameters to be estimated, randomly initialized
    omegaParameters = np.random.normal([0, 0, 0, 0], [1, 1, 1, 1])
    #render flag
    render = False
    # Define place holders for the problem
    #lists to store experience
    probabilitiesEpisode, actionsEpisode, rewardsEpisode, weightedRewardsEpisode, gradients = [], [], [], [], []
    states = state
    episodeNumber = 0
    while episodeNumber < MAX_EPISODES:
        if rewardSum > 190 or render == True:
            environment.render()
            render = True
        probabilities = getProbability(omegaParameters, state)
        #pick action given the probabilities, using binomial density
        # p(t), a(t), r(t), s(t) are calculated
        action = 1 if probabilities > np.random.uniform() else 0
        #get the state, reward and if the agent failed from the environment
        state, reward, done, _ = environment.step(action)
        #add the reward to the sum of rewardsEpisode
        rewardSum += reward
        # Concatenate probabilities, action and reward for the episode
        probabilitiesEpisode.append(probabilities)
        actionsEpisode.append(action)
        rewardsEpisode.append(reward)
        #Verifies if the episode is over
        if done:
            episodeNumber += 1
            weightedRewardsEpisode = getWeightedRewards(rewardsEpisode)
            #normalize rewards
            if len(gradients) == 0:
                #if its the first gradient
                gradients = getGradientLoss(actionsEpisode, probabilitiesEpisode, weightedRewardsEpisode, states).mean(axis=0)
            else:
                #if its the second or more gradient, stack the vector, once per batch
                gradients = np.vstack((gradients, getGradientLoss(actionsEpisode, probabilitiesEpisode, weightedRewardsEpisode, states).mean(axis=0)))
            if episodeNumber % BATCH_SIZE == 0:
                #the average gradient for the batch is used for omega update
                omegaParameters = omegaParameters - LEARNING_RATE * gradients.mean(axis=0)
                gradients = []
                print("Average reward for episode", rewardSum / BATCH_SIZE)
                if rewardSum / BATCH_SIZE >= 200:
                    print("Problem solved!")
                rewardSum = 0
            # Reset all
            state = environment.reset()
            probabilitiesEpisode, actionsEpisode, rewardsEpisode, weightedRewardsEpisode = [], [], [], []
            states = state
        else:
            states = np.vstack((states, state))

    environment.close()

if __name__ == "__main__":
    trainAndRunModel()