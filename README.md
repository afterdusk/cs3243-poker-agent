# Group 23 - Yairboi

**CS3243 Introduction to Artificial Intelligence - Term Project**

A project which develops an agent that can play a simplified version of poker.

## Project overview

In this project, we aim to develop multiple competing players (i.e. the things that actually play poker) with different player algorithms. These players can be trained with different training algorithms. A training algorithm is assigned to train a player type in a pairing called a playerspace. We also loosely use the term playerspace to mean the training algorithm itself.

### Players

There are 3 main classes of players:

* Linear player. These use a simple evaluation function to decide what action to take. In this repo, these players are named with Greek letters.
* Minimax player
* Neural player

### Training algorithms

#### Training playerspaces

* David's playerspace. A DIY and somewhat arbitrary genetic-ish algorithm is used. Players are initialized with random weights and made to play against each other. A number of winning bots (i.e. initialized players) are chosen to "reproduce" and to clone themselves, and the remaining bots are replaced with new randomly initialized players. After a certain number of generations have passed, or if the bots have converged, a predetermined set of winning bots (which we have trained in previous rounds) is injected into the pool and allowed to compete and reproduced with the bots that have been trained. With this algorithm, we ensure that we explore the space of possible players while helping the newly trained bots beat our previous bests.
* Liang Jun's playerspace. This is a copy of David's playerspace which was adapted to train the minimax players. It uses the same approach.
* CMA-ES playerspace. This uses https://en.m.wikipedia.org/wiki/CMA-ES where the utility function is expected win rate against all other bots in the same playerspace.
* RRT playerspace

#### Non-training playerspaces

* Profile playerspace. Among other things, this generates data that can be used to make graphs for our report. Data is output to the `profile` folder.
* Botlympics. As we train players separately, we need a way to gauge their performance relative to each other. In the Botlympics, we take a set of bots and play a number of games against each other. On a single core, each game takes roughly 3 minutes to complete. Game specifications are obtained from `agentboards/Botlympics.csv`, and game results are output to `agentboards/Botlympics Matrix.csv`.

### Misc

* agentboards: Contains the Botlympics config and results, as well as all of David's and LJ playerspace results
* archives: Files that are no longer needed
* bigbrainstats: CS3243 course tournament results, downloaded by a cronjob every 10 minutes.
* report: LaTeX files for our project report.

## Paralellization across the Compute Cluster

As our computations are very CPU intensive but embarrassingly parallel, we are able to easily parallelize our training.

TODO: Data flow with and without

TODO: Client allocation

## Set up

Set up Python 2.7 and Python 3.7. In your Python 2 environment, install `paho-mqtt`, `numpy`, and `cython`. On your computer, also install Eclipse's Mosquitto broker.

We also use [PyPokerEngine](https://ishikota.github.io/PyPokerEngine/) which is included in the starter code.

## Running

Before running anything, be sure to `cd OMPEval` and run `make`.

### During development

Use the `example.py` file to run new players/bots locally to ensure that they work.

### Training in parallel

Prerequisites: Install the Mosquitto broker. You can use Linuxbrew for this. I'd also recommend installing and using Tmux to manage your multiple shell instances and to easily persist them even after you terminate your SSH session.

If you're running this on a compute cluster, you'll need to SSH into an compute cluster node. When outside SoC, you can run `ssh -J username@sunfire.comp.nus.edu.sg xcna1`.

If you're running this on your computer, you may have to change some things manually as the scripts have only been tested on the compute cluster. Things that may go wrong include the client start script, which will try to start another Mosquitto broker that links to our main broker running on the xcna1 cluster node, and the client kill script, which will kill all Python and Mosquitto processes started by your user account.

1. Optionally start a Tmux session.
1. Perform the following steps in separate shells (easy in Tmux):
    1. Mosquttto broker: Start the Mosquitto broker by running `mosquitto`.
    1. Game server
        1. Optionally Cythonize your code by running `python setup.py build_ext --inplace`.
        1. Run `python SERVER_script.py`.
    1. Game clients
        1. `cd cluster_runner`
        1. Run `./node_manage.sh countcpu`.
        1. Once `SERVER_script.py` prints `CONNECTED`, run `./node_manage.sh start`.
1. While running, you can run `cluster_runner/print_load.sh` to see the load averages of all the compute cluster machines.
1. To stop everything:
    1. Mosquitto broker: Simply press Ctrl+c to terminate the broker. You don't need to do this when restarting the clients and servers.
    1. Game server: Also simply press Ctrl+c to terminate the server script.
    1. Game clients:
        1. Press Ctrl+c to terminate the SSH clients
        1. Run `./node_manage.sh kill` to SSH into all the compute cluster nodes and `killall python mosquitto` on them.
    
Note that it is necessary to start the server before the clients, and to restart the clients whenever the server is restarted.

## Poker engine details

Obtained from the starter repo's instructions.

### Create your own player
#### Example player

```

class RaisedPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    #Implement your code
    return action

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass
```
#### Example Game
The example game is in the example.py

#### Information for the game
```valid_actions```: vaild action list


```
[
    { "action" : "fold"  },
    { "action" : "call" },
    { "action" : "raise" }
]
OR 
[
    {"action": "fold"},
    {"action": "call"}
]
```

In the limited version, user only allowed to raise for four time in one round game.    
In addition, in each street (preflop,flop,turn,river),each player only allowed to raise for four times.

Other information is similar to the PyPokerEngine,please check the detail about the parameter [link](https://github.com/ishikota/PyPokerEngine/blob/master/AI_CALLBACK_FORMAT.md)
