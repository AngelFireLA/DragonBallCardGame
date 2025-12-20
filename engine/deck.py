import random

class Deck:
    def __init__(self, cards):
        self.cards = cards

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, num=1):
        drawn_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return drawn_cards

    def reset(self):
        for card in self.cards:
            card.reset()
        random.shuffle(self.cards)

    def add_cards(self, cards):
        self.cards.extend(cards)