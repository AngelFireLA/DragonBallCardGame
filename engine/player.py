import random

from engine.deck import Deck
from engine.support import Support
from utils import max_active_fighters, load_fighters, load_supports
from engine.fighter import Fighter
class Player:
    def __init__(self, name):
        self.name: str = name
        self.hand: list = []
        self.active_fighters: list[Fighter] = []
        self.remaining_hp: int = 100000
        self.remaining_ki: int = 0
        self.deck: Deck = Deck()


    def reset(self):
        self.hand.clear()
        self.active_fighters.clear()
        self.deck.reset()
        self.remaining_hp = 100000
        self.remaining_ki = 0

    def get_chosen_card(self, choice_type: str, options: list):
        # temporary
        return random.choice(options)


    def get_active_fighter_names(self):
        return [fighter.name for fighter in self.active_fighters]

    def get_playable_fighters(self):
        playable_fighters = []
        for card in self.hand:
            if isinstance(card, Fighter) and (card.cost <= self.remaining_ki or (card.reduced_cost and not card.previous_form)):
                fusion_ready = all(any(member in af.name and card.form_level <= af.form_level for af in self.active_fighters) for member in card.fusion_members)
                print(card.fusion_members, [af.name and card.form_level <= af.form_level for af in self.active_fighters], fusion_ready)
                if (card.fusion_members and fusion_ready) or (card.previous_form and any(card.previous_form in af.name and card.form_level > af.form_level for af in self.active_fighters)):
                    playable_fighters.append(card)
                elif not card.previous_form and not card.fusion_members:
                    playable_fighters.append(card)

        return playable_fighters

    def get_playable_supports_in_hand(self):
        return [card for card in self.hand if isinstance(card, Support) and card.cost <= self.remaining_ki]

    def setup_turn(self, battle):
        print("Cards in hand : ")
        print("- " + "\n- ".join([str(card) for card in self.hand]))
        print("Remaining KI:", self.remaining_ki, "Remaining HP:", self.remaining_hp)
        chosen_action = input("Choose action - Play (F)ighter, Play (S)upport, (E)nd turn: ").strip().upper()
        while chosen_action != "E":
            if chosen_action == 'F':
                if len(self.active_fighters) >= max_active_fighters:
                    print("Maximum active fighters reached.")
                else:
                    playable_fighters = self.get_playable_fighters()
                    if not playable_fighters:
                        print("No fighters available to play.")
                    else:
                        print("Available fighters to play:")
                        for idx, fighter in enumerate(playable_fighters):
                            print(f"{idx}:", fighter)
                        try:
                            choice = int(input(f"Enter fighter index to play: "))
                            if 0 <= choice < len(playable_fighters):
                                selected_fighter = playable_fighters[choice]

                                self.hand.remove(selected_fighter)
                                if not selected_fighter.previous_form and not selected_fighter.fusion_members:
                                    self.active_fighters.append(selected_fighter)
                                    if not selected_fighter.reduced_cost:
                                        self.remaining_ki -= selected_fighter.cost
                                elif selected_fighter.previous_form and any(selected_fighter.previous_form in af.name and selected_fighter.form_level > af.form_level for af in self.active_fighters):
                                    possible_fighters = [af for af in self.active_fighters if
                                                         selected_fighter.previous_form in af.name and selected_fighter.form_level > af.form_level]
                                    # select the fighter witht he lowest health+attack power
                                    possible_fighters.sort(key=lambda f: (f.max_health + f.attack_power))
                                    to_replace = possible_fighters[0]
                                    if to_replace.form_level > 0:
                                        self.remaining_ki += to_replace.cost
                                    self.remaining_ki -= selected_fighter.cost
                                    self.active_fighters.append(selected_fighter)
                                    self.active_fighters.remove(to_replace)
                                elif selected_fighter.fusion_members:
                                    fusion_fighters = {member: [] for member in selected_fighter.fusion_members}
                                    for af in self.active_fighters:
                                        if af.name in fusion_fighters:
                                            fusion_fighters[af.name].append(af)
                                    for member in selected_fighter.fusion_members:
                                        # remove the fighter with the lowest health+attack power
                                        fusion_fighters[member].sort(key=lambda f: (f.max_health + f.attack_power))
                                        to_remove = fusion_fighters[member][0]
                                        self.active_fighters.remove(to_remove)
                                    self.active_fighters.append(selected_fighter)
                                else:
                                    raise ValueError("Cannot play this fighter yet.")
                                print(f"{self.name} played {selected_fighter.name}.")
                            else:
                                print("Invalid choice. Try again.")
                        except ValueError as e:
                            print("Invalid input. Please enter a number.", e)

                chosen_action = input("Choose action - Play (F)ighter, Play (S)upport, (E)nd turn: ").strip().upper()
            elif chosen_action == 'S':
                supports = self.get_playable_supports_in_hand()
                if not supports:
                    print("No support cards available in hand.")
                else:
                    print("Available supports to play:")
                    for idx, support in enumerate(supports):
                        print(f"{idx}:", support)
                    try:
                        choice = int(input(f"Enter support index to play: "))
                        if 0 <= choice < len(supports):
                            selected_support = supports[choice]
                            self.hand.remove(selected_support)
                            selected_support.apply_effect(battle, self)
                            self.remaining_ki -= selected_support.cost
                            print(f"{self.name} played support {selected_support.name}.")
                        else:
                            print("Invalid choice. Try again.")
                    except ValueError as e:
                        print("Invalid input. Please enter a number.", e)

                chosen_action = input("Choose action - Play (F)ighter, Play (S)upport, (E)nd turn: ").strip().upper()
            else:
                print("Invalid action. Please choose again.")
                chosen_action = input("Choose action - Play (F)ighter, Play (S)upport, (E)nd turn: ").strip().upper()