"""
Main Entry Point
Run this file to start the game
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game_engine import GameEngine


def main():
    """Main function"""
    game = GameEngine()
    game.run()


if __name__ == "__main__":
    main()
