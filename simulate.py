import gym
import beer_game_env



env = gym.make('BeerGame-v0', n_agents=4, env_type='classical')

env.reset()
for _ in range(1000):
     env.render()
     env.step([0,0,0,1])  # take a random action