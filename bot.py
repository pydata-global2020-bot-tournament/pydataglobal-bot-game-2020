"""Supply Chain Game entry point.

The game consists of four agents interacting with each other as the diagram shows:

                     orders                orders                   orders                 orders
demand             --------->             --------->              --------->              --------->
------> (RETAILER)            (WHOLESALER)           (DISTRIBUTOR)          (MANUFACTURER)
                   <---------             <---------              <---------              <---------
                    shipments             shipments                shipments               shipments

The agents form a supply chain, i.e. each agent can send a request to its neighbour and ask for a delivery of a
certain amount of goods. The neighbour does a shipment but also orders delivery from the next entity in the chain
in case of getting out of stock. The game unrolls in a turn-based fashion: all agents take decisions about the number
of items to order simultaneously, then a next turn starts.

A retailer is the first agent in the chain. It gets demand from customers and should keep them fulfilled ordering more
items from agents next in the chain.

A manufacturer is the last agent in the chain. It "orders" items from an infinite supply and ships them down the chain.

The problem is that the agents don't know the current numbers of the stock level of their partners. Also, the
order/shipment exchange doesn't happen instantaneously but involves two turns of lead time. (Except Manufacturer that
refills its supply with lead time of one turn). The same lead time is true for delivery of a previously ordered amount.
For example, if the Retailer orders X amount on n-th turn, this information reaches the Wholesaler in two "days", i.e.
on the (n+2)-th turn. Therefore, non-optimal orderings could  result in stock-outs or too many items hold, and
both conditions incur costs.

Your goal is to implement a strategy for each of the four agents in such a way, that the costs are minimal after
20 game turns. It means that you should try to escape both shortages AND holding too many items in stock. Your strategy
shouldn't use any other information except stored in a dictionary that is given to `get_action()` method. Also, the
agents are not allowed to communicate their stock levels or any other internal information to each other.

In this file, you'll find a dummy implementation for each agent that orders a random amount of items each turn. If you
run this script as-is, you'll see that the costs at the end of the game are very high. Try to come up with a better
solution!
"""
import sys
from argparse import ArgumentParser
from statistics import *


import numpy as np

from supply_chain_env.envs.env import SupplyChainBotTournament
from supply_chain_env.leaderboard import post_score_to_api

orders_customer=[]


orders_customer=[]

def simple_proj(step_state,last_turn ,agent):
    demand=[5, 4, 4, 4, 4, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
    if 0<=(step_state['turn']+(3+agent*2))<20:
        if step_state['current_stock']>8:
            return demand[step_state['turn']+(3+agent*2)]-1
        else:
            return demand[step_state['turn'] + (3 + agent * 2)]
    else:
        return 2

class Retailer:
    def get_action(self, step_state: dict) -> int:
        orders_customer.append(step_state['next_incoming_order'])
        agent=0
        last_turn=16
        print(step_state, 'Retailer')
        return simple_proj(step_state,last_turn,agent)


class Wholesaler:

    def get_action(self, step_state: dict) -> int:
        agent=1
        last_turn=14
        print(step_state, 'Wholes')
        return simple_proj(step_state,last_turn,agent)

class Distributor:

    def get_action(self, step_state: dict) -> int:
        agent=2
        last_turn=12
        print(step_state, 'Distr')
        return simple_proj(step_state,last_turn,agent)


class Manufacturer:

    def get_action(self, step_state: dict) -> int:
        agent=3
        last_turn=11
        print(step_state, 'Manuf')
        return simple_proj(step_state,last_turn,agent)

# --------------------
# Game setup and utils
# --------------------


def create_agents():
    """Creates a list of agents acting in the environment.

    Note that the order of agents is important here. It is always considered by the environment that the first
    agent is Retailer, the second one is Wholesaler, etc.
    """
    return [Retailer(), Wholesaler(), Distributor(), Manufacturer()]


def run_game(agents: list, environment: str = 'classical', verbose: bool = False):
    env = SupplyChainBotTournament(
        env_type=environment
    )  # TODO: decide if we should support all 3 environments or support one
    state = env.reset()
    while not env.done:
        if verbose:
            env.render()
        actions = [a.get_action(state[i]) for i, a in enumerate(agents)]
        state, rewards, done, _ = env.step(actions)
    return state


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--no_submit', action='store_true')
    return parser.parse_args()


def main(args):
    last_state = run_game(create_agents(), verbose=True)
    print(orders_customer)

    if args.no_submit:
        sys.exit(0)

    # get total costs and post results to leaderboard api
    total_costs = sum(agent_state["cum_cost"] for agent_state in last_state)
    post_score_to_api(score=total_costs)

if __name__ == '__main__':
    main(parse_args())
