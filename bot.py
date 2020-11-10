import gym
from beer_game_env.envs import BeerGame
import numpy as np
from enum import Enum, auto
from beer_game_env.leaderboard import post_score_to_api

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
    
    # get total costs and post results to leaderboard api
    total_costs = 0
    for step in step_state:
        total_costs += step['cum_cost']
    post_score_to_api(score=total_costs)
