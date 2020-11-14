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

import numpy as np
from scipy import stats

from supply_chain_env.envs.env import SupplyChainBotTournament
from supply_chain_env.leaderboard import post_score_to_api

class BaseVendor():
    def __init__(self):
        self.orders = []
        self.stock = []
    def get_action(self, step_state: dict) -> int:
        # Save Order history
        if step_state["next_incoming_order"] > 0:
            self.orders.append(step_state["next_incoming_order"])
        
        # Median Filter
        num_order = 5
        median_orders = np.median(self.orders)
        if len(self.orders) > num_order:
            median_orders = np.median(self.orders[-num_order:])

            # detect linear trend
            slope, intercept, _, _, _ = stats.linregress(list(range(len(self.orders))), self.orders)

            next_order = np.median([intercept + slope*len(self.orders), median_orders, self.orders[-1]]) + slope

        else:
            next_order = self.orders[-1] + 2

        return int(max(0, next_order))  # provide your implementation here

# [{'current_stock': -9, 'turn': 19, 'cum_cost': 273.0, 'inbound_shipments': [8, 11], 'orders': [37, 41], 'next_incoming_order': 8}, {'current_stock': -207, 'turn': 19, 'cum_cost': 1065.5, 'inbound_shipments': [12, 17], 'orders': [205, 232], 'next_incoming_order': 37}, {'current_stock': -472, 'turn': 19, 'cum_cost': 1057.5, 'inbound_shipments': [29, 42], 'orders': [181, 338], 'next_incoming_order': 205}, {'current_stock': -69, 'turn': 19, 'cum_cost': 206.5, 'inbound_shipments': [55, 63], 'orders': [82], 'next_incoming_order': 181}]

class Retailer(BaseVendor):
    def __init__(self):
        super().__init__()


class Wholesaler(BaseVendor):
    def __init__(self):
        super().__init__()


class Distributor(BaseVendor):
    def __init__(self):
        super().__init__()


class Manufacturer(BaseVendor):
    def __init__(self):
        super().__init__()


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
    all_costs = []
    for _ in range(30):
        last_state = run_game(create_agents(), verbose=True)
        all_costs.append(sum(agent_state["cum_cost"] for agent_state in last_state))

    if args.no_submit:
        sys.exit(0)

    # get total costs and post results to leaderboard api
    total_costs = np.median(all_costs)
    post_score_to_api(score=total_costs)

def train_bots(args):
    score_history = []

    if args.no_submit:
        sys.exit(0)

    for i in range(30):
        last_state = run_game(create_agents(), verbose=False)
        score = sum(agent_state["cum_cost"] for agent_state in last_state)
        score_history.append(score)
        print('episode ', i, 'score %.2f' % score, 'trailing 100 games avg %.3f' % np.mean(score_history[-100:]))

    return score_history

if __name__ == '__main__':

    #scores = train_bots(parse_args())
    #print(scores)
    #print(np.mean(scores))
    #print(np.median(scores))

    main(parse_args())
