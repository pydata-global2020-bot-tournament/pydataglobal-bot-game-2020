import gym
from beer_game_env.envs import BeerGame
import numpy as np
from enum import Enum, auto

class AgentType(Enum):
    Retailer = auto()
    Wholesaler = auto()
    Distributor = auto()
    Manufacturer = auto()

class Agent(object):
    def __init__(self, agent_type: AgentType):
         self.agent_type = agent_type
    
    def get_action(self, step_state: dict):
        return np.random.randint(0, 4)  # random order
        # your decision logic goes there!


if __name__ == '__main__':
    env = BeerGame(env_type='classical') #TODO: decide if we should support all 3 environments or support one
    done = False
    agents = [Agent(t) for t in AgentType]
    step_state = env.reset()
    while not done:
        env.render()
        actions = [a.get_action(step_state[i]) for i, a in enumerate(agents)]
        step_state, step_rewards, done, _ = env.step(actions)

