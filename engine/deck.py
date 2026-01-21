import random

from utils import load_fighters, load_supports


class Deck:
    def __init__(self, all_cards=None):
        self.all_cards = load_fighters() + load_supports() if all_cards is None else all_cards
        random.shuffle(self.all_cards)
        self.cards = self.all_cards.copy()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, num=1):
        drawn_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return drawn_cards

    def reset(self):
        self.cards = self.all_cards.copy()
        random.shuffle(self.cards)

    def add_cards(self, cards):
        self.cards.extend(cards)

    def get_card_of_name(self, name):
        # returns the card if an exact name match is in the remaining deck, otherwise None
        for card in self.cards:
            if card.name == name:
                return card
        return None

    def remove(self, card):
        if card in self.cards:
            self.cards.remove(card)