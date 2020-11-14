# Supply Chain Bot Tournament

Supply Chain Bot Tournament implemented as an OpenAI Gym environment.

The core part of the game environment's implementation was copied from [this repository](https://github.com/orlov-ai/beer-game-env). 

## Installation

1. Ask for contrubtion permissions from anyone at [this mattermost channel](https://forum.numfocus.org/pydata-global/channels/supply-chain-bot-tournament) or the BY booth (bottom right in gather).

2. Create a new conda environment to keep things clean
```
conda create python=3.6 --name supply-chain-env
source activate supply-chain-env
```

3. Clone the repository
```
git clone https://github.com/pydata-global2020-bot-tournament/pydataglobal-bot-game-2020.git
```

4. Install the package
```
cd supply-chain-env
pip install -e .
```

5. Launch the `bot.py` file to run the game with randomly behaving agents
```
python bot.py --no_submit
``` 

If everything was setup properly, you'll see a bunch of messaged printed to the standard output
showing agents' actions and their outcomes.

## Implementing Your Solution

In order to implement your solution, open the `bot.py` file and provide your implementation
for all given agents. You don't need to change anything except agents' classes. Also, please 
note that a valid agent's strategy cannot peek into the game's environment state or communicate 
internal state to other agents! (See the docstring at the very beginning of the file for 
additional details).  

To test your implementation, run the `bot.py` script again. The better your solution works, the
smaller should be the total cost reported at the end of the game.

## Submitting to the Leaderboard

In order to participate in the tournament, you should follow these steps:
1. Once you're happy with the developed strategy, post your changes to a new branch in this repository 
to trigger the evaluation and open a PR to merge to `master`
2. GitHub Actions will take care of evaluating your implementation and post your results to the leaderboard
3. Update your branch as often as you like, but be aware that the most recent results will be updated
to the leaderboard, irrespectively of the result

Good luck and have fun!
