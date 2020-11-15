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

from supply_chain_env.envs.env import SupplyChainBotTournament
from supply_chain_env.leaderboard import post_score_to_api

from pathlib import Path
from datetime import datetime
RUNDATE = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Best parameters: costs ~72
PARAMETERS = [47, 8, 16, 8, 33, 8, 12, 8]

"""
step_state
----------
  current_stock : int
    amount of items in stock.
    Each turn, the first item of inbound_shipments will be added and
    next_incomming_order will be subtracted.
  turn : int
    current turn?
  cum_cost : float
    cost for current overstock
  inbound_shipments : list[int]
    amount of products in bound. The list is two long as it takes
    two days to get the products.
  orders : list[int]
    current open orders. The list is two long as it takes two days
    to make the order.
    Each turn the right item [1] will be pushed to the right of
    inbound items.
  next incomming order : int
    amount of items sold this round
"""


class DemandPredicter:

    def __init__(self, stock_threshold=8, amount_to_buy=4):
        self.order_history = []
        self.simulation = RUNDATE
        self.STOCK_THRESHOLD = stock_threshold
        self.AMOUNT_TO_BUY = amount_to_buy

    def predict_demands_same_stategy(self, n_demands=3):
        """
        Predict demand by copying the last demand n_demands times.
        """
        order_history = self.order_history[:]
        last_demand = order_history[-1]
        for ix in range(n_demands):
            order_history.append(last_demand)
        return order_history[-3:]

    def get_order(self, step_state: dict, agent_name: str) -> int:
        # collect data
        current_stock = step_state['current_stock']
        inbound_shipments = step_state['inbound_shipments']
        next_incoming_order = step_state['next_incoming_order']
        orders = step_state['orders']
        self.order_history.append(next_incoming_order)

        # demand will be average of last four turns
        average_demand = np.mean(self.order_history[-4:])
        demand = [next_incoming_order] + 3 * [average_demand]

        # incomming shipments from previous orders
        if len(orders) == 1:
            # Manufacturer only have lead time of one day
            orders = [0] + orders
        inbound = inbound_shipments + [orders[1]] + [orders[0]]

        # approximate stock
        stock = [None, None, None, None]
        stock[0] = current_stock + inbound[0] - demand[0]
        stock[1] = stock[0] + inbound[1] - demand[1]
        stock[2] = stock[1] + inbound[2] - demand[2]
        stock[3] = stock[2] + inbound[3] - demand[3]

        # order
        if stock[3] < self.STOCK_THRESHOLD:
            order = self.AMOUNT_TO_BUY
        else:
            order = 0

        return order


class Retailer(DemandPredicter):

    def get_action(self, step_state: dict) -> int:
        return self.get_order(step_state, 'Retailer')


class Wholesaler(DemandPredicter):

    def get_action(self, step_state: dict) -> int:
        return self.get_order(step_state, 'Retailer')


class Distributor(DemandPredicter):

    def get_action(self, step_state: dict) -> int:
        return self.get_order(step_state, 'Retailer')


class Manufacturer(DemandPredicter):

    def get_action(self, step_state: dict) -> int:
        return self.get_order(step_state, 'Retailer')


def create_agents_with_settings(x : list):
    """Creates a list of agents acting in the environment.

    Note that the order of agents is important here. It is always considered by the environment that the first
    agent is Retailer, the second one is Wholesaler, etc.
    """
    return [
        Retailer(x[0], x[1]),
        Wholesaler(x[2], x[3]),
        Distributor(x[4], x[5]),
        Manufacturer(x[6], x[7]),
    ]

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
    last_state = run_game(
        create_agents_with_settings(PARAMETERS),
        verbose=True,
    )

    if args.no_submit:
        sys.exit(0)

    # get total costs and post results to leaderboard api
    total_costs = sum(agent_state["cum_cost"] for agent_state in last_state)
    post_score_to_api(score=total_costs)


if __name__ == '__main__':
    main(parse_args())
