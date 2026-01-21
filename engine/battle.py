import random

from engine.fighter import Fighter
from engine.player import Player
from utils import initial_hand_size, initial_ki_amount, cards_drawn_per_turn, ki_gained_per_turn, load_supports, \
    load_fighters


class Battle:
    def __init__(self, player1, player2):
        self.player1: Player = player1
        self.player2: Player = player2
        self.turn = 0



    def do_players_attacks(self):
        print("Attacks phase:")
        print("Player 1 fighters attacking:", self.player1.active_fighters)
        self.do_attacks(self.player1, self.player2)
        print("Player 2 fighters attacking:", self.player2.active_fighters)
        self.do_attacks(self.player2, self.player1)

    def start(self, run=True):
        self.player1.reset()
        self.player2.reset()

        self.player1.hand = self.player1.deck.draw(initial_hand_size)
        self.player2.hand = self.player2.deck.draw(initial_hand_size)
        self.player1.remaining_ki = initial_ki_amount
        self.player2.remaining_ki = initial_ki_amount
        if run: self.run()

    def recharge(self):
        self.player1.hand.extend(self.player1.deck.draw(cards_drawn_per_turn))
        self.player2.hand.extend(self.player1.deck.draw(cards_drawn_per_turn))
        self.player1.remaining_ki += ki_gained_per_turn
        self.player2.remaining_ki += ki_gained_per_turn

    def players_setup_turn(self):
        self.player1.setup_turn(self)
        self.player2.setup_turn(self)

    def run(self):
        while True:
            self.turn += 1
            print(f"Turn {self.turn} begins.")
            self.recharge()
            self.players_setup_turn()
            self.do_players_attacks()
            if self.player1.remaining_hp <= 0 or self.player2.remaining_hp <= 0:
                if self.player1.remaining_hp <= 0 and self.player2.remaining_hp <= 0:
                    print("It's a draw!")
                elif self.player1.remaining_hp <= 0:
                    print(f"{self.player2.name} wins!")
                else:
                    print(f"{self.player1.name} wins!")
                return
            self.update_players_remaining_fighters()
            print(f"Turn {self.turn} ends.\n")

    def update_players_remaining_fighters(self):
        self.player1.active_fighters = [f for f in self.player1.active_fighters if f.is_alive()]
        self.player2.active_fighters = [f for f in self.player2.active_fighters if f.is_alive()]

        for card in self.player1.hand + self.player2.hand:
            if isinstance(card, Fighter):
                card.reduced_cost = False

        for card in self.player1.active_fighters:
            if isinstance(card, Fighter):
                if not card.is_ozaru or card.temporary_health_shield <= 0:
                    card.temporary_health_shield = 0
                    card.temporary_attack_boost = 1
                    for tag in card.temporary_tags:
                        card.tags.remove(tag)
                    card.temporary_tags = []
                    if card.is_ozaru and "Goku" in card.name and card.form_level < 4:
                        goku_ssj4 = self.player1.deck.get_card_of_name("Goku SSJ4")
                        if goku_ssj4 is not None:
                            self.player1.active_fighters.append(goku_ssj4)
                            self.player1.active_fighters.remove(card)
                    card.is_ozaru = False

        for card in self.player2.active_fighters:
            if isinstance(card, Fighter):
                if not card.is_ozaru or card.temporary_health_shield <= 0:
                    card.temporary_health_shield = 0
                    card.temporary_attack_boost = 1
                    for tag in card.temporary_tags:
                        card.tags.remove(tag)
                    card.temporary_tags = []
                    if card.is_ozaru and "Goku" in card.name and card.form_level < 4:
                        goku_ssj4 = self.player2.deck.get_card_of_name("Goku SSJ4")
                        if goku_ssj4 is not None:
                            self.player2.active_fighters.append(goku_ssj4)
                            self.player2.active_fighters.remove(card)
                    card.is_ozaru = False
    def do_attacks(self, attacker, defender):
        for fighter in attacker.active_fighters:
            damage = fighter.attack_power
            damage = int(damage*fighter.temporary_attack_boost)

            if not defender.active_fighters:
                defender.remaining_hp -= damage
            else:
                opponent_fighter = random.choice(defender.active_fighters)
                if opponent_fighter.temporary_health_shield > 0:
                    opponent_fighter.temporary_health_shield = max(0,  opponent_fighter.temporary_health_shield-damage)
                    if opponent_fighter.temporary_health_shield == 0:
                        print(f"{opponent_fighter.name}'s temporary health shield is broken!")
                else:
                    opponent_fighter.current_health -= damage

                print(f"{fighter.name} attacks {opponent_fighter.name} for {fighter.attack_power} damage.")
                if opponent_fighter.current_health < 0:
                    defender.remaining_hp -= abs(opponent_fighter.current_health)
                    defender.active_fighters.remove(opponent_fighter)

