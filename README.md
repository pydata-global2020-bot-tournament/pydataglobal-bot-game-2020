# Supply Chain Bot Tournament
Supply Chain Bot Tournament implemented as an OpenAI Gym environment.

Installation:

1. Create a new conda environment to keep things clean
```
conda create python=3.6 --name supply-chain-env
source activate supply-chain-env
```

2. Clone the environment repository
```
git clone https://github.com/lr4d/pydataglobal-bot-game-2020.git
```

3. Point to root repository and install the package
```
cd supply-chain-env
pip install -e .
```

To use:
```
import gym
import supply_chain_env
env = gym.make('SupplyChainTournament-v0', n_agents=4, env_type='classical')
```

tested with gym version `gym==0.17.3`

Need a feature? Have a problem? Just start an issue.
PRs are always welcome.
