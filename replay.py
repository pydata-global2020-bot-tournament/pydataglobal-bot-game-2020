"""A helper tool to debug agents behavior.

The tool renders agents states and actions using pyglet UI.
"""
import argparse
import json
from collections import OrderedDict
from typing import Optional, Tuple, List, Dict

import numpy as np
import pyglet
from dataclasses import dataclass

from bot import AgentType


class Drawable:

    def update(self, dt: float): pass

    def draw(self): pass


WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
DEFAULT_AGENT_SIZE = (300, 200)
DEFAULT_AGENT_COLOR = (0, 0, 0)
DEFAULT_AGENT_LABEL_COLOR = (0, 0, 255, 255)

AGENT_STATE_LABELS = OrderedDict([
    ('stock_level', 'stocks'),
    ('next_incoming_orders', 'demand'),
    ('holding_cost', 'holding cost (turn)'),
    ('cumulative_holding_cost', 'holding cost (acc)'),
    ('stockout_cost', 'stock-out cost (turn)'),
    ('cumulative_stockout_cost', 'stock-out cost (acc)')
])


@dataclass
class Agent(Drawable):
    name: str
    supply: int = 0
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = DEFAULT_AGENT_SIZE
    top_label: bool = False
    sprite_color: Tuple[int, int, int] = DEFAULT_AGENT_COLOR
    label_color: Tuple[int, int, int, int] = DEFAULT_AGENT_LABEL_COLOR
    sprite: Optional[pyglet.shapes.Rectangle] = None
    agent_name: Optional[pyglet.text.Label] = None
    state_labels: Optional[OrderedDict] = None

    def __post_init__(self):
        self.sprite = pyglet.shapes.Rectangle(*self.position,
                                              *self.size,
                                              color=self.sprite_color)

        self.agent_name = pyglet.text.Label(text=self.name,
                                            x=self.sprite.x + self.sprite.width//2,
                                            y=self.sprite.y,
                                            anchor_x='center',
                                            anchor_y='top',
                                            font_size=16,
                                            color=self.label_color,
                                            font_name='monospace')

        self.state_labels = OrderedDict([
            (
                label_name,
                pyglet.text.Label(
                    anchor_x='left',
                    anchor_y='top',
                    font_size=12,
                    font_name='monospace',
                    color=(255, 255, 255, 255)
                )
             )
            for label_name in AGENT_STATE_LABELS.keys()
        ])

        self.update_state({})

    def update_state(self, state: Dict):
        for name, verbose_name in AGENT_STATE_LABELS.items():
            info = state.get(name, np.nan)
            label = self.state_labels[name]
            label.text = f'{verbose_name}: {info}'
            if name == 'stock_level' and not np.isnan(info) and int(info) <= 0:
                label.color = (255, 0, 0, 255)
            else:
                label.color = (255, 255, 255, 255)

    def set_center(self, x: int, y: int):
        self.sprite.x = x - self.sprite.width//2
        self.sprite.y = y - self.sprite.height//2

    def get_center(self) -> Tuple[int, int]:
        return self.sprite.x + self.sprite.width//2, self.sprite.y + self.sprite.height//2

    def draw(self):
        self.sprite.draw()
        self.agent_name.draw()
        for label in self.state_labels.values():
            label.draw()

    def update(self, dt: float):
        self.agent_name.x = self.sprite.x + self.sprite.width // 2
        self.agent_name.y = self.sprite.y
        if self.top_label:
            self.agent_name.y += (self.sprite.height + self.agent_name.content_height)
        height = self.sprite.height - 10
        for label in self.state_labels.values():
            label.x = self.sprite.x + 10
            label.y = self.sprite.y + height
            height -= label.content_height


@dataclass
class Layout(Drawable):
    agents: List[Agent]
    window_size: Tuple[int, int]

    def __post_init__(self):
        assert len(self.agents) == 4

        w, h = self.window_size
        retailer, wholesaler, distribution, manufacturer = self.agents

        retailer.set_center(1. / 4 * w, 1. / 4 * h)
        wholesaler.set_center(3. / 4 * w, 1. / 4 * h)
        distribution.set_center(3. / 4 * w, 3. / 4 * h)
        manufacturer.set_center(1. / 4 * w, 3. / 4 * h)

        x1, y1 = retailer.get_center()
        x2, y2 = wholesaler.get_center()
        x1 += retailer.sprite.width // 2
        x2 -= wholesaler.sprite.width // 2
        retailer_to_wholesaler = pyglet.shapes.Line(x1, y1, x2, y2, width=10, color=(200, 0, 32))
        retailer_to_wholesaler_orders_label = pyglet.text.Label(
            x=w//2,
            y=1./4*h + 30,
            font_size=14,
            font_name='monospace',
            text='orders >',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='top',
        )
        retailer_to_wholesaler_orders_value = pyglet.text.Label(
            x=x1 + 30,
            y=y1 + 30,
            font_size=14,
            font_name='monospace',
            text=str([1, 4]),
            color=(0, 0, 255, 255),
            anchor_x='left',
            anchor_y='top'
        )
        retailer_to_wholesaler_shipments_label = pyglet.text.Label(
            x=w//2,
            y=1./4*h - 30,
            font_size=14,
            font_name='monospace',
            text='< shipments',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='bottom'
        )
        retailer_to_wholesaler_shipments_value = pyglet.text.Label(
            x=x2 - 30,
            y=y1 - 30,
            font_size=14,
            font_name='monospace',
            text=str([1, 4]),
            color=(0, 0, 255, 255),
            anchor_x='right',
            anchor_y='bottom'
        )

        x1, y1 = wholesaler.get_center()
        x2, y2 = distribution.get_center()
        y1 += wholesaler.sprite.height // 2
        y2 -= distribution.sprite.height // 2
        wholesaler_to_distribution = pyglet.shapes.Line(x1, y1, x2, y2, width=10, color=(200, 0, 32))
        wholesaler_to_distribution_orders_label = pyglet.text.Label(
            x=3./4*w - 90, y=1./2*h,
            font_size=14,
            font_name='monospace',
            text='orders /\\',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='center'
        )
        wholesaler_to_distribution_orders_value = pyglet.text.Label(
            x=x1 - wholesaler.sprite.width//4,
            y=y1,
            font_size=14,
            font_name='monospace',
            text='some',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='bottom'
        )
        wholesaler_to_distribution_shipments_label = pyglet.text.Label(
            x=3. / 4 * w + 90,
            y=1. / 2 * h,
            font_size=14,
            font_name='monospace',
            text='\\/ shipments',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='center'
        )
        wholesaler_to_distribution_shipments_value = pyglet.text.Label(
            x=x1 + wholesaler.sprite.width//4,
            y=y2,
            font_size=14,
            font_name='monospace',
            text='some',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='top'
        )

        x1, y1 = distribution.get_center()
        x2, y2 = manufacturer.get_center()
        x1 -= distribution.sprite.width // 2
        x2 += manufacturer.sprite.width // 2
        distribution_to_manufacturer = pyglet.shapes.Line(x1, y1, x2, y2, width=10, color=(200, 0, 32))
        distribution_to_manufacturer_orders_label = pyglet.text.Label(
            x=w // 2, y=3. / 4 * h + 30,
            font_size=14,
            font_name='monospace',
            text='< orders',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='top',
        )
        distribution_to_manufacturer_orders_value = pyglet.text.Label(
            x=x1 - 30,
            y=y1 + 30,
            text='n/a',
            font_size=14,
            font_name='monospace',
            color=(0, 0, 255, 255),
            anchor_x='right',
            anchor_y='top',
        )
        distribution_to_manufacturer_shipments_label = pyglet.text.Label(
            x=w // 2, y=3. / 4 * h - 30,
            font_size=14,
            font_name='monospace',
            text='shipments >',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='bottom',
        )
        distribution_to_manufacturer_shipments_value = pyglet.text.Label(
            x=x2 + 30,
            y=y1 - 30,
            text='n/a',
            font_size=14,
            font_name='monospace',
            color=(0, 0, 255, 255),
            anchor_x='left',
            anchor_y='bottom'
        )

        x1, y1 = manufacturer.get_center()
        y1 += manufacturer.sprite.height // 2
        x2, y2 = x1, h
        manufacturer_to_dummy = pyglet.shapes.Line(x1, y1, x2, y2, width=10, color=(200, 0, 32))
        manufacturer_to_dummy_orders_label = pyglet.text.Label(
            x=x1 - manufacturer.sprite.width//4,
            y=h - 30,
            font_size=14,
            font_name='monospace',
            text='orders /\\',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='center'
        )
        manufacturer_to_dummy_orders_value = pyglet.text.Label(
            x=x1 - manufacturer.sprite.width//4,
            y=y1,
            font_size=14,
            font_name='monospace',
            text='n/a',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='bottom'
        )
        manufacturer_to_dummy_shipments_label = pyglet.text.Label(
            x=x1 + manufacturer.sprite.width//4,
            y=h - 30,
            font_size=14,
            font_name='monospace',
            text='\\/ shipments',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='center'
        )
        manufacturer_to_dummy_shipments_value = pyglet.text.Label(
            x=x1 + manufacturer.sprite.width//4,
            y=y1,
            font_size=14,
            font_name='monospace',
            text='n/a',
            color=(0, 0, 255, 255),
            anchor_x='center',
            anchor_y='bottom'
        )

        self._primitives = [
            retailer_to_wholesaler,
            wholesaler_to_distribution,
            distribution_to_manufacturer,
            manufacturer_to_dummy,
        ]

        self._transactions = OrderedDict([
            ('retailer_orders_label', retailer_to_wholesaler_orders_label),
            ('retailer_orders_value', retailer_to_wholesaler_orders_value),
            ('retailer_shipments_label', retailer_to_wholesaler_shipments_label),
            ('retailer_shipments_value', retailer_to_wholesaler_shipments_value),

            ('wholesaler_orders_label', wholesaler_to_distribution_orders_label),
            ('wholesaler_orders_value', wholesaler_to_distribution_orders_value),
            ('wholesaler_shipments_label', wholesaler_to_distribution_shipments_label),
            ('wholesaler_shipments_value', wholesaler_to_distribution_shipments_value),

            ('distributor_orders_label', distribution_to_manufacturer_orders_label),
            ('distributor_orders_value', distribution_to_manufacturer_orders_value),
            ('distributor_shipments_label', distribution_to_manufacturer_shipments_label),
            ('distributor_shipments_value', distribution_to_manufacturer_shipments_value),

            ('manufacturer_orders_label', manufacturer_to_dummy_orders_label),
            ('manufacturer_orders_value', manufacturer_to_dummy_orders_value),
            ('manufacturer_shipments_label', manufacturer_to_dummy_shipments_label),
            ('manufacturer_shipments_value', manufacturer_to_dummy_shipments_value)
        ])

        self._curr_turn = pyglet.text.Label(
            x=1./4 * w, y=10, font_size=16, font_name='monospace',
            anchor_x='center',
            text='n/a', color=(0, 0, 0, 255))

        self._curr_loss = pyglet.text.Label(
            x=3. / 4 * w, y=10, font_size=16, font_name='monospace',
            anchor_x='center',
            text='n/a', color=(0, 0, 0, 255))

    def draw(self):
        for agent in self.agents:
            agent.draw()
        for primitive in self._primitives:
            primitive.draw()
        for label in self._transactions.values():
            label.draw()
        self._curr_turn.draw()
        self._curr_loss.draw()

    def update(self, dt: float):
        for agent in self.agents:
            agent.update(dt)

    def update_state(self, env_state: Dict):
        for i, agent in enumerate(self.agents):
            agent_state = {key: env_state[key][i] for key in AGENT_STATE_LABELS.keys()}
            agent.update_state(agent_state)
            orders = env_state['orders_placed'][i]
            if agent.name == 'retailer':
                orders = list(reversed(orders))
            self._transactions[f'{agent.name}_orders_value'].text = str(orders)
            self._transactions[f'{agent.name}_shipments_value'].text = str(env_state['inbound_shipments'][i])
        loss = sum(env_state["cumulative_holding_cost"] + env_state["cumulative_stockout_cost"])
        self._curr_turn.text = f'turn: {env_state["turn"]}'
        self._curr_loss.text = f'cost: {loss:.2f} EUR'


class SupplyChainWindow(pyglet.window.Window):  # noqa

    def __init__(self, agents: List[Agent], history: List[Dict], **window_kwargs):
        window_kwargs.update({'width': WINDOW_WIDTH, 'height': WINDOW_HEIGHT})
        super().__init__(**window_kwargs)
        self.layout = Layout(agents, window_size=(self.width, self.height))
        self.history = history
        self.curr_state = 0
        pyglet.gl.glClearColor(1, 1, 1, 1)
        pyglet.clock.schedule_interval(self.update, 1./60)

    def on_draw(self):
        self.clear()
        self.layout.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            self.curr_state = max(0, self.curr_state - 1)
        elif symbol == pyglet.window.key.RIGHT:
            self.curr_state = min(len(self.history) - 1, self.curr_state + 1)

    def update(self, dt: float):
        self.layout.update(dt)
        env_state = self.history[self.curr_state]
        self.layout.update_state(env_state)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file',
                        default='/tmp/history.json',
                        help='Environment history')
    return parser.parse_args()


def main(args: argparse.Namespace):
    agents = [Agent(agent_type.name.lower()) for agent_type in AgentType]
    _, _, distribution, _ = agents
    distribution.top_label = True
    with open(args.input_file) as fp:
        history = json.load(fp)
    window = SupplyChainWindow(agents, history)
    pyglet.app.run()


if __name__ == '__main__':
    main(parse_args())

