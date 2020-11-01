import gym
from beer_game_env.envs import BeerGame
import numpy as np

if __name__ == '__main__':
    env = BeerGame(n_agents=4, env_type='classical')
    env.reset()
    done = False
    while not done:
        env.render()
        actions = np.random.uniform(0, 16, size=4)
        actions = actions.astype(int)
        step_state, step_rewards, done, _ = env.step(actions)

    # you can also save and load environment via
    # canned_env = env._save()
    # env._load(canned_env)
