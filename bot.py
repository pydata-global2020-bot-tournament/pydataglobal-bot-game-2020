import gym
from beer_game_env.envs import BeerGame
import numpy as np


class Agent:

    def player_actions(self):
        "Return 4 actions as numpy array for each agent: brewery, distributor, wholesaler, retailer."
        "This function can be modified or new functions can also be introduced in Agent class"
        "by competitor."
        actions = np.random.uniform(0, 16, size=4)
        actions = actions.astype(int)
        return actions


if __name__ == '__main__':
    env = BeerGame(env_type='classical') #TODO: decide if we should support all 3 environments or support one
    env.reset()
    done = False
    while not done:
        env.render()
        agent = Agent()
        actions = agent.player_actions() # returns 4 random int as numpy array as of now
        step_state, step_rewards, done, _ = env.step(actions)

