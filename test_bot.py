from bot import AgentType, Agent
from beer_game_env.envs import BeerGame
import numpy as np

class TestAgent(Agent):
    def __init__(self, AgentType):
        self.counter = 0
    def get_action(self, step_state: dict):
        self.counter += 1
        return 4  # always the same action, 4


def test_bot():
    env = BeerGame(env_type='classical') #TODO: decide if we should support all 3 environments or support one
    done = False
    agents = [TestAgent(t) for t in AgentType]
    step_state = env.reset()
    while not done:
        env.render()
        actions = [a.get_action(step_state[i]) for i, a in enumerate(agents)]
        step_state, step_rewards, done, _ = env.step(actions)
        assert actions == [4,4,4,4]
