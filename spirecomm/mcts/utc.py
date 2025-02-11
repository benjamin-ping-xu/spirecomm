# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a
# state.GetRandomMove() or state.DoRandomRollout() function.
#
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in
# the UCTPlayGame() function at the bottom of the code.
#
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
#
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
#
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
import random

from spirecomm.spire.character import PlayerClass
from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent, ScreenType


class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic
        zero-sum game, although they can be enhanced and made quicker, for example by using a
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """

    def __init__(self):
        self.playerJustMoved = 2  # At the root pretend the player just moved is player 2 - player 1 has the first move

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = GameState()
        st.playerJustMoved = self.playerJustMoved
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        self.playerJustMoved = 3 - self.playerJustMoved

    def GetMoves(self):
        """ Get all possible moves from this state.
        """

    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm.
        """

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


class SpireState:
    """
    A state of the game Slay the Spire
    """

    def __init__(self, game, coord):
        self.game_state = game
        self.coordinator = coord

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = SpireState(self.game_state, self.coordinator)
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
        """
        # TODO: connect with SpireComm to implement game state change

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        # TODO: connect with SpireComm to get valid moves

    def GetResult(self):
        """ Get the game result.
        """
        # TODO: connect with SpireComm to identify game win or loss
        if self.coordinator.last_game_state.screen_type == ScreenType.GAME_OVER:
            if self.coordinator.last_game_state.screen.victory:
                return 1.0
            else:
                return -1.0
        else:
            return 0.0
        # if self.game_state.screen_type == ScreenType.GAME_OVER:
        #     if self.game_state.screen.victory:
        #         return 1.0
        #     else:
        #         return -1.0
        # else:
        #     return 0.0

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """

    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves()  # future child nodes
        self.playerJustMoved = state.playerJustMoved  # the only part of the state that the Node needs later

    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key=lambda c: c.wins / c.visits + sqrt(2 * log(self.visits) / c.visits))[-1]
        return s

    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=m, parent=self, state=s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose=False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []:  # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.DoMove(m)
            node = node.AddChild(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []:  # while state is non-terminal
            # TODO: change to use ForgottenArbiter AI for rollout
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None:  # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(
                node.playerJustMoved))  # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if (verbose):
        print(rootnode.TreeToString(0))
    else:
        print(rootnode.ChildrenToString())

    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


def UCTPlayGame(agent, coor, sd, char):
    """
     Play Slay the Spire on A20, Specific Seed
     UCT iterations (= simulations = tree nodes).
     :param agent: Agent class for actions
     :type agent: SimpleAgent
     :param coor: Coordinator for actions
     :type coor: Coordinator
     :param sd: seed for run
     :type sd: str
     :param char: character to use
     :type char: PlayerClass
    """
    state = SpireState(coor.last_game_state, coor)
    agent.change_class(char)
    coor.game_setup(char, 20, sd)

    result = coor.game_loop()
    state = SpireState(coor.last_game_state, coor)

    print("Game Result: " + str(state.GetResult()))
    if result:
        print("Victory!")
    else:
        print("Defeat :(")
    #
    # while state.GetMoves() != []:
    #     m = UCT(rootstate=state, itermax=100, verbose=False)
    #     print("Best Move: " + str(m) + "\n")
    #     state.DoMove(m)
    # if state.GetResult() == 1.0:
    #     print("Victory!")
    # else:
    #     print("Defeat :(")
