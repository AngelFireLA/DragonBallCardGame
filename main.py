from engine.player import Player
from engine.battle import Battle

player1 = Player("Player 1")
player2 = Player("Player 2")

battle = Battle(player1, player2)
battle.start()
