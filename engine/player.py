from engine.deck import Deck
from utils import max_active_fighters
from engine.fighter import Fighter
class Player:
    def __init__(self, name):
        self.name: str = name
        self.deck: Deck = None
        self.hand: list = []
        self.discard_pile: list = []
        self.active_fighters: list[Fighter] = None
        self.remaining_hp: int = 100000
        self.remaining_ki: int = 0

    def reset(self):
        self.deck.cards.extend(self.hand)
        self.hand.clear()
        self.deck.cards.extend(self.discard_pile)
        self.discard_pile.clear()
        self.deck.cards.extend(self.active_fighters)
        self.active_fighters.clear()
        self.remaining_hp = 100000
        self.remaining_ki = 0
        self.deck.reset()

    def set_deck(self, deck: Deck):
        self.deck = deck

    def draw(self, num=1):
        drawn_cards = self.deck.draw(num)
        self.hand.extend(drawn_cards)

    def get_active_fighter_names(self):
        return [fighter.name for fighter in self.active_fighters]

    def get_playable_fighters(self):
        playable_fighters = []
        for card in self.hand:
            if isinstance(card, Fighter) and card.cost <= self.remaining_ki:
                fusion_ready = all(any(member in af.name and card.form_level <= af.form_level for af in self.active_fighters) for member in card.fusion_members)
                if (card.fusion_members and fusion_ready) or (card.previous_form and any(card.previous_form in af.name and card.form_level > af.form_level for af in self.active_fighters)):
                    playable_fighters.append(card)
                elif not card.previous_form and not card.fusion_members:
                    playable_fighters.append(card)

        return playable_fighters

    def setup_turn(self, battle):
        print("Cards in hand : ", "\n- ".join([str(card) for card in self.hand]))
        chosen_action = input("Choose action - (P)lay fighter, (E)nd turn: ").strip().upper()
        while chosen_action == 'P' and len(self.active_fighters) < max_active_fighters:
            print("Available fighters to play:")
            for idx, fighter in enumerate(self.hand):
                if fighter in self.get_playable_fighters():
                    print(f"{idx}:", fighter)
            try:
                choice = int(input(f"Enter fighter index to play: "))
                if 0 <= choice < len(self.hand):
                    selected_fighter = self.hand[choice]
                    playable_fighters = self.get_playable_fighters()
                    if selected_fighter in playable_fighters:
                        self.hand.remove(selected_fighter)
                        if not selected_fighter.previous_form and not selected_fighter.fusion_members:
                            self.active_fighters.append(selected_fighter)
                            self.remaining_ki -= selected_fighter.cost
                        elif selected_fighter.previous_form in self.active_fighters:
                            possible_fighters = [af for af in self.active_fighters if selected_fighter.previous_form in af.name and selected_fighter.form_level > af.form_level]
                            # select the fighter witht he lowest health+attack power
                            possible_fighters.sort(key=lambda f: (f.max_health + f.attack_power))
                            to_replace = possible_fighters[0]
                            if to_replace.form_level > 0:
                                self.remaining_ki += to_replace.cost
                            self.remaining_ki -= selected_fighter.cost
                            self.active_fighters.append(selected_fighter)
                            self.active_fighters.remove(to_replace)
                        elif selected_fighter.fusion_members:
                            fusion_fighters = {member.name: [] for member in selected_fighter.fusion_members}
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
                        print("Selected card is not a valid fighter or prerequisites not met.")
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            if len(self.active_fighters) >= max_active_fighters:
                print("Maximum active fighters reached.")
                break
            chosen_action = input("Choose action - (P)lay fighter, (E)nd turn: ").strip().upper()