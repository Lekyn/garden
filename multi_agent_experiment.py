from pybrain.rl.experiments import Experiment

class Multi_Agent_Experiment(Experiment):
    
    def __init__(self, task, agent_list):
        self.task = task
        self.agent_list = agent_list
        self.stepid = 0

    def _oneInteraction(self):
        self.stepid += 1
        for a in range(len(self.agent_list)):
            agent = self.agent_list[a]
            agent.integrateObservation(self.task.getObservation())
            self.task.performAction(agent.getAction())
            reward = self.task.getReward()
            agent.giveReward(reward)

class Continuous_MA_Experiment(Multi_Agent_Experiment):

    def doInteractionsAndLearn(self, number = 1):
        for x in range(number):
            self._oneInteraction()
            for a in range(len(self.agent_list)):
                self.agent_list[a].learn()


class Continuous_MA_Experiment_Tako(Continuous_MA_Experiment):

    def __init__(self, task, tako_list):
        self.task = task
        self.tako_list = tako_list
        self.stepid = 0

    def doInteractionsAndLearn(self, number = 1):
        for x in range(number):
            self._oneInteraction()
            for a in range(len(self.tako_list)):
                self.tako_list[a].agent.learn()

    def _oneInteraction(self):
        self.stepid += 1
        for a in range(len(self.tako_list)):
            tako = self.tako_list[a]
            tako.agent.integrateObservation(self.task.getObservation(tako))
            self.task.performAction(tako.agent.getAction(), tako)
            reward = self.task.getReward(tako)
            tako.agent.giveReward(reward)
            
