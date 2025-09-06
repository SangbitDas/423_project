🚀 Endless Runner 3D (PyOpenGL)

A simple 3D endless runner game written in Python with PyOpenGL and GLUT.
The player runs along a road, dodging obstacles, collecting coins, and picking up power-ups like magnets and a hoverboard.

Features include jumping, sliding, hoverboard mode, first-person/third-person camera toggle, and an  enemy chaser.

🎮 Features

1. Endless Forward Movement – The player moves forward automatically in a lane, creating an endless runner experience.

2. Lane Switching & Player Movement – Move left or right between lanes, jump over obstacles, or slide under low barriers, with simple running/jumping animations.

3. Obstacle Spawning – Randomly generate obstacles in lanes; collision with obstacles reduces player life.

4. Collectibles & Score System – Coins, gems, or items appear along the track; collecting them increases score, which also considers distance traveled.

5. Life System & Restart Option – Player has a limited number of lives; collisions reduce life, and the game can be restarted without closing the window.

6. Speed Scaling – Forward movement speed gradually increases, providing progressively higher difficulty.

7. Power-Ups – Temporary boosts like shield (invincibility), magnet (auto-collect), or double score appear along the track.


8. Dynamic Camera System – Smoothly follows the player; allows adjustable views and first-person perspective for immersive gameplay.

9. Visual Feedback & HUD – Display current score, remaining lives, and collected power-ups on screen using on-screen text.

10. Invisible Enemy Chase – An enemy is always chasing the player but not shown on screen. If the player makes a mistake (collision or missed jump/slide), the enemy closes in for 5 seconds, increasing pressure and risk of losing.


11. Multiple Levels – The game has two distinct levels:
Level 1: Player moves normally with the vehicle.


Level 2: Player moves in a cart, introducing different handling, speed, and movement style for variety

🖥️ Requirements

Make sure you have Python 3.8+ and install dependencies:

pip install PyOpenGL PyOpenGL_accelerate


▶️ Running the Game"

python <gamename>.py


How to make it a copyable table in readme.md
| Key           | Action                              |
| ------------- | ----------------------------------- |
| **A /   | Move Left                           |
| **D  | Move Right                          |
| **Space**     | Jump (Normal Mode)/ Fast run (Hoverboard mode) |
| **S**         | Slide                               |
| **C**         | Toggle Hoverboard Mode              |
| **F**         | Toggle First-Person Camera          |
| **R**         | Restart Game                        |
