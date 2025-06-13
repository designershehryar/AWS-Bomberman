# Bomberman Game

A simple Bomberman game built with Python and Pygame.

## How to Play

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the game:
   ```
   python bomberman.py
   ```

## Controls

- **Arrow Keys**: Move the player (one press = one step)
- **Space**: Place a bomb

## Game Rules

- Navigate through the maze and use bombs to destroy blocks
- Defeat all enemies to win the game
- Avoid getting caught in bomb explosions
- Avoid touching enemies
- You have 3 lives - the game ends when all lives are lost
- Earn 100 points for each enemy defeated
- Earn bonus points (200 per remaining life) when completing a level

## Features

- Player movement with collision detection (one key press = one step)
- Bomb placement and explosions with animated bombs
- Destructible and indestructible blocks
- Different monster types with unique appearances and animations
- Lives system with player respawning
- Scoring system
- Sound effects and background music
- Win condition when all enemies are defeated
- Game over state with final score display

## Sound Effects

The game includes the following sound effects:
- Background music
- Bomb placement
- Explosions
- Enemy death
- Player death
- Game over
- Victory

You can replace the placeholder sound files in the `assets/sounds` directory with your own sound files to customize the game experience.