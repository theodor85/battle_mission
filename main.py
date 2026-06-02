import sys
import os

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

from app.game import Game

if __name__ == "__main__":
    Game().run()
