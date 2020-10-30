import gym
from beer_game_env.envs import BeerGame
import numpy as np

if __name__ == '__main__':
    env = BeerGame(n_agents=4, env_type='classical')
    start_state = env.reset()
    for i, obs in enumerate(start_state):
        print(f'Agent {i} observation: {obs}')
    env.render()
    done = False
    while not done:
        actions = np.random.uniform(0, 16, size=4)
        actions = actions.astype(int)
        step_state, step_rewards, done, _ = env.step(actions)
        #print(step_state, step_rewards, done)
        env.render()

    # you can also save and load environment via
    # canned_env = env._save()
    # env._load(canned_env)
