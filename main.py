import itertools
import datetime
import sys

from spirecomm.communication.coordinator import Coordinator
from spirecomm.ai.agent import SimpleAgent
from spirecomm.spire.character import PlayerClass

from spirecomm.mcts import utc

if __name__ == "__main__":
    agent = SimpleAgent()
    coordinator = Coordinator()
    coordinator.signal_ready()
    coordinator.register_command_error_callback(agent.handle_error)
    coordinator.register_state_change_callback(agent.get_next_action_in_game)
    coordinator.register_out_of_game_callback(agent.get_next_action_out_of_game)

    # Play on specific seed on Ironclad
    utc.UCTPlayGame(agent, coordinator, "2M8NQL6W44C4Z", PlayerClass.IRONCLAD)

    # # Play games forever, cycling through the various classes
    # for chosen_class in itertools.cycle(PlayerClass):
    #     agent.change_class(chosen_class)
    #     result = coordinator.play_one_game(chosen_class)
