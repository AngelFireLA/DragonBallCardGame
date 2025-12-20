import random

from engine.player import Player
from utils import initial_hand_size, initial_ki_amount, cards_drawn_per_turn, ki_gained_per_turn


class Battle:
    def __init__(self, player1, player2):
        self.player1: Player = player1
        self.player2: Player = player2
        self.turn = 0

    def start(self):
        self.player1.reset()
        self.player2.reset()

        self.player1.hand = self.player1.deck.draw(initial_hand_size)
        self.player2.hand = self.player2.deck.draw(initial_hand_size)
        self.player1.remaining_ki = initial_ki_amount
        self.player2.remaining_ki = initial_ki_amount

        while True:
            self.turn += 1
            print(f"Turn {self.turn} begins.")
            self.player1.draw(cards_drawn_per_turn)
            self.player2.draw(cards_drawn_per_turn)
            self.player1.remaining_ki += ki_gained_per_turn
            self.player2.remaining_ki += ki_gained_per_turn
            self.player1.setup_turn(self)
            self.player2.setup_turn(self)
            if not self.player1.active_fighters or not self.player2.active_fighters:
                if not self.player1.active_fighters:
                    print(f"{self.player2.name} wins!")
                elif not self.player2.active_fighters:
                    print(f"{self.player1.name} wins!")
                else:
                    print("It's a draw!")
                break
            self.do_attacks(self.player1, self.player2)
            self.do_attacks(self.player2, self.player1)

            self.player1.active_fighters = [f for f in self.player1.active_fighters if f.is_alive()]
            self.player2.active_fighters = [f for f in self.player2.active_fighters if f.is_alive()]
            print(f"Turn {self.turn} ends.\n")

    def do_attacks(self, attacker, defender):
        for fighter in attacker.active_fighters:
            opponent_fighter = random.choice(defender.active_fighters)
            opponent_fighter.current_health -= fighter.attack_power
            print(f"{fighter.name} attacks {opponent_fighter.name} for {fighter.attack_power} damage.")
            if not opponent_fighter.is_alive():
                print(f"{opponent_fighter.name} has been defeated!")
                attacker.score += opponent_fighter.value


