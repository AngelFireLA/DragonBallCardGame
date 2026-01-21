from engine.player import Player
from engine.deck import Deck
from engine.battle import Battle
from utils import generate_interesting_decks, load_fighters, load_supports
deck1 = Deck(generate_interesting_decks(load_fighters(), load_supports(), 10))
deck2 = Deck(generate_interesting_decks(load_fighters(), load_supports(), 10))

player1 = Player("Player 1", deck1)
player2 = Player("Player 2", deck2)

battle = Battle(player1, player2)
battle.start()
