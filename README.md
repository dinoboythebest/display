# # Handheld RPG Console

## About the Project

The Handheld RPG Console is a small, custom-built gaming device designed to play a simple RPG using a Raspberry Pi Pico. The goal is to create a portable console with a screen, physical buttons, and custom hardware.

The console uses a Raspberry Pi Pico RP2040 as its main controller and a 1.54-inch ST7789 LCD display. The controls consist of six buttons: Up, Down, Left, Right, A, and B.

## How It Works

The Raspberry Pi Pico will read button inputs and use them to control the game. The directional buttons are used to move the player around the map, while A is used to interact with objects and B is used to open or close the inventory.

The RPG software is being developed in Python. Current game features include player movement, map boundaries, walls, treasure chests, an inventory system, health points, and turn-based battle mechanics.

The display will show the game, while the custom PCB will connect the Pico, screen, and buttons together.

## Hardware

- Raspberry Pi Pico RP2040
- 1.54-inch ST7789 LCD display (240 × 240)
- Six tactile buttons
- Custom-designed PCB
- USB connection for programming and power

## Controls

| Button | Function |
|---|---|
| Up | Move up / navigate menu |
| Down | Move down / navigate menu |
| Left | Move left |
| Right | Move right |
| A | Confirm / interact / attack |
| B | Open inventory / go back |

## Project Images

### PCB Design

<img width="1920" height="1080" alt="Screenshot 2026-11-01 at 4 44 25 PM" src="https://github.com/user-attachments/assets/3b7f5040-b70f-4374-b088-8a76f5534e7f" />

### Display and Wiring
<img width="1920" height="1080" alt="Screenshot 2026-11-01 at 4 44 30 PM" src="https://github.com/user-attachments/assets/3611d4bd-b0b4-460e-8ee4-7660e4d78a3c" />


## Firmware

The game software is being developed in Python.

