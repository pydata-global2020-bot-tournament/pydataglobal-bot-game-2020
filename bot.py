import argparse
import sys
from enum import Enum, auto

import numpy as np

from supply_chain_env.envs.env import SupplyChainBotTournament
from supply_chain_env.leaderboard import post_score_to_api


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    # TODO: decide if we should support all 3 environments or support one
    parser.add_argument('--env_name',
                        default='classical',
                        choices=['classical', 'uniform_0_2', 'normal_10_4'])
    parser.add_argument('--no_submit', action='store_true')
    parser.add_argument('--save_history', action='store_true')
    parser.add_argument('--history_file', default='/tmp/history.json')
    return parser.parse_args()


def main(args: argparse.Namespace):
    env = SupplyChainBotTournament(
        env_type="classical"
    )  # TODO: decide if we should support all 3 environments or support one
    agents = [Agent(t) for t in AgentType]
    step_state = env.reset()

    while not env.done:
        env.render()
        actions = [a.get_action(step_state[i]) for i, a in enumerate(agents)]
        step_state, step_rewards, done, _ = env.step(actions)

    if args.save_history:
        env.save_history(args.history_file)

    if args.no_submit:
        # don't submit a solution to the leaderboard
        sys.exit(0)
    else:
        # get total costs and post results to leaderboard api
        total_costs = 0
        for step in step_state:
            total_costs += step['cum_cost']

        post_score_to_api(score=total_costs)


if __name__ == '__main__':
    main(parse_args())
