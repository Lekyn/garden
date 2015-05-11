
from garden import Garden
from pybrain.rl.environments import Task
from numpy import floor
from tako import Tako
from widget import *

class GardenTask(Task):
    last_action = None
    
    def performAction(self, action, tako):
        index = self.find_action(action)
        self.last_action = index
        result = self.env.performAction(index, tako)
        tako.modify(result)
    
    def getReward(self, tako):
        reward = 0
        hung_diff = tako.hunger - tako.last_hunger
        bor_diff = tako.boredom - tako.last_boredom
        pain_diff = tako.pain - tako.last_pain
        if hung_diff > 0:
            reward = -(hung_diff/2)
        elif bor_diff > 0:
            reward = -(bor_diff/3)
        elif bor_diff < -0.5:
            reward = 0 - (bor_diff)
        elif pain_diff > 0:
            reward = 0 - (pain_diff)
        if tako.pain > 0 and pain_diff <= 0:
            reward -= tako.pain/2
        return reward

    def find_action(self, action):
        highest = 0
        for i in range(len(action)):
            if action[highest] < action[i]:
                highest = i
        return highest

    def getObservation(self, tako):
        obs = self.env.getSensors(tako)
        nobs = self.transform_obs(obs)
        nobs.append(tako.hunger)
        nobs.append(tako.boredom)
        nobs.append(tako.pain)
        return nobs

    def transform_obs(self, obs):
        normed = [0, 0, 0, 0, 0]
        for i in range(len(obs)):
            x = obs[i].node
            normed[x] += 0.5
            if i == 1:
                normed[x] += 0.5
        return normed
        
            
        
