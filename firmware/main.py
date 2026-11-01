
import machine
import st7789
import time
import random

# Handheld RPG Console

# variables for the screen and tile sizes
WIDTH = 240
HEIGHT = 240
TILE = 32
MAP_VIEW_ROWS = 6
HUD_Y = 208

# sets up the display using SPI and connects it to the correct pico pins
spi = machine.SPI(
    0,
    baudrate=40000000,
    polarity=1,
    phase=1,
    sck=machine.Pin(18),
    mosi=machine.Pin(19)
)

tft = st7789.ST7789(
    spi,
    WIDTH,
    HEIGHT,
    reset=machine.Pin(21, machine.Pin.OUT),
    dc=machine.Pin(20, machine.Pin.OUT),
    cs=machine.Pin(17, machine.Pin.OUT),
    backlight=machine.Pin(22, machine.Pin.OUT),
    rotation=0
)

# button dictionary connects each physical button to its gpio pin
# pull up makes the button normally read 1 and read 0 when pressed

buttons = {
    "UP": machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP),
    "LEFT": machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP),
    "RIGHT": machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP),
    "DOWN": machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP),
    "A": machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP),
    "B": machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
}

# variables for the player and game
player_x = 5
player_y = 5

player_hp = 20
max_hp = 20

enemy_hp = 15
enemy_max_hp = 15

in_battle = False
menu_open = False
menu_selection = 0
inventory = []

# map uses numbers to represent different tiles
# 0 = grass, 1 = wall, 2 = chest, 3 = enemy

starting_map = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,0,0,0,0,1],
    [1,0,0,1,3,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,2,1],
    [1,1,1,1,1,1,1,1,1,1]
]

# creates a copy of the original map so it can be restored when restarting
game_map = [row.copy() for row in starting_map]

# colours used to draw the different tiles and objects
BLACK = st7789.BLACK
WHITE = st7789.WHITE
GREEN = st7789.GREEN
RED = st7789.RED
BROWN = 0xA145
DARK_GREEN = 0x2385
GREY = 0x8410
YELLOW = 0xFFE0
BLUE = 0x001F


# checks if the player can move to a certain position
# stops the player from walking into walls, enemies or outside the map
def can_move(x, y):
    if x < 0 or x >= 10 or y < 0 or y >= 10:
        return False

    if game_map[y][x] == 1 or game_map[y][x] == 3:
        return False

    return True


# draws the different tiles on the screen depending on their number
# each tile is 32 by 32 pixels
def draw_tile(x, y, tile):
    px = x * TILE
    py = y * TILE

    if tile == 0:
        tft.fill_rect(px, py, TILE, TILE, GREEN)
        tft.fill_rect(px + 5, py + 8, 3, 3, DARK_GREEN)

    elif tile == 1:
        tft.fill_rect(px, py, TILE, TILE, GREY)
        tft.fill_rect(px, py, TILE, 3, WHITE)

    elif tile == 2:
        tft.fill_rect(px, py, TILE, TILE, GREEN)
        tft.fill_rect(px + 7, py + 10, 18, 16, BROWN)
        tft.fill_rect(px + 7, py + 10, 18, 4, YELLOW)

    elif tile == 3:
        tft.fill_rect(px, py, TILE, TILE, GREEN)
        tft.fill_rect(px + 6, py + 8, 20, 19, BLUE)
        tft.fill_rect(px + 10, py + 13, 4, 4, WHITE)
        tft.fill_rect(px + 19, py + 13, 4, 4, WHITE)


# draws the player on the screen using coloured rectangles
# this is a temporary sprite until the actual player sprite is added
def draw_player(x, y):
    px = x * TILE
    py = y * TILE

    tft.fill_rect(px + 9, py + 5, 14, 10, YELLOW)
    tft.fill_rect(px + 8, py + 15, 16, 13, RED)


# draws the map one row at a time using the tile numbers
# the camera follows the player and the hud displays their health and potions
def draw_map():
    tft.fill(BLACK)

    # camera follows the player when they move around the map
    camera_y = max(0, min(player_y - 3, 10 - MAP_VIEW_ROWS))

    for screen_y in range(MAP_VIEW_ROWS):
        world_y = camera_y + screen_y

        for x in range(10):
            draw_tile(x, screen_y, game_map[world_y][x])

    # draws the player at their position on the screen
    screen_player_y = player_y - camera_y
    draw_player(player_x, screen_player_y)

    # displays the player's health and potion count at the bottom
    tft.fill_rect(0, HUD_Y, WIDTH, 32, BLACK)
    tft.text("HP: {}/{}".format(player_hp, max_hp), 5, 214, WHITE)
    tft.text("POTIONS: {}".format(inventory.count("Potion")), 5, 228, YELLOW)


# checks if the player has a potion and if their health is not full
# if they do it restores 10 health and removes one potion from inventory
def use_potion():
    global player_hp

    if "Potion" not in inventory:
        return

    elif player_hp == max_hp:
        return

    else:
        player_hp = min(player_hp + 10, max_hp)
        inventory.remove("Potion")


# draws the inventory menu and displays the available options
# the player can use up and down to select and A to confirm
def draw_menu():
    draw_map()

    tft.fill_rect(25, 55, 190, 115, BLACK)
    tft.text("INVENTORY", 55, 65, WHITE)

    options = [
        "Potion x{}".format(inventory.count("Potion")),
        "Back"
    ]

    for i, option in enumerate(options):
        color = YELLOW if i == menu_selection else WHITE
        tft.text(option, 45, 100 + i * 25, color)


# checks the four tiles around the player to see if there is an enemy
# returns the position of the enemy if one is found
def nearby_enemy():
    positions = [
        (player_x, player_y - 1),
        (player_x, player_y + 1),
        (player_x - 1, player_y),
        (player_x + 1, player_y)
    ]

    for x, y in positions:
        if 0 <= x < 10 and 0 <= y < 10:
            if game_map[y][x] == 3:
                return x, y

    return None


# checks if an enemy is next to the player and starts a battle
# resets the enemy's health when a battle begins
def start_battle():
    global in_battle, enemy_hp

    if nearby_enemy() is not None:
        in_battle = True
        enemy_hp = enemy_max_hp


# controls one turn of the battle
# A makes the player attack and B allows the player to run away
# if the enemy survives it attacks the player back
def battle_turn(action):
    global enemy_hp, player_hp, in_battle

    if action == "B":
        in_battle = False
        return

    if action != "A":
        return

    damage = random.randint(3, 7)
    enemy_hp -= damage

    if enemy_hp <= 0:
        position = nearby_enemy()

        if position:
            x, y = position
            game_map[y][x] = 0

        enemy_hp = enemy_max_hp
        in_battle = False
        return

    enemy_damage = random.randint(1, 4)
    player_hp -= enemy_damage

    if player_hp <= 0:
        game_over()


# called when the player's health reaches zero
# gives the player the choice to restart the game or quit
# restarting restores the player's health, inventory and original map
def game_over():
    global player_x, player_y, player_hp
    global enemy_hp, in_battle, menu_open
    global menu_selection, inventory, game_map

    tft.fill(BLACK)
    tft.text("GAME OVER", 65, 80, RED)
    tft.text("A = RESTART", 65, 115, WHITE)
    tft.text("B = QUIT", 65, 145, WHITE)

    while True:
        if buttons["A"].value() == 0:
            player_x = 5
            player_y = 5
            player_hp = max_hp
            enemy_hp = enemy_max_hp
            in_battle = False
            menu_open = False
            menu_selection = 0
            inventory = []
            game_map = [row.copy() for row in starting_map]

            time.sleep_ms(250)
            return

        elif buttons["B"].value() == 0:
            tft.fill(BLACK)

            while True:
                time.sleep(1)

        time.sleep_ms(30)


# turns the physical button presses into game actions
# checks what button was pressed and performs the correct action
def handle_button(action):
    global player_x, player_y
    global menu_open, menu_selection

    # battle system takes priority while a battle is happening
    if in_battle:
        battle_turn(action)
        return

    # inventory menu controls
    if menu_open:
        if action == "UP":
            menu_selection = (menu_selection - 1) % 2

        elif action == "DOWN":
            menu_selection = (menu_selection + 1) % 2

        elif action == "A":
            if menu_selection == 0:
                use_potion()

            else:
                menu_open = False

        elif action == "B":
            menu_open = False

        return

    # moves the player around the map if there are no obstacles
    if action == "UP" and can_move(player_x, player_y - 1):
        player_y -= 1

    elif action == "DOWN" and can_move(player_x, player_y + 1):
        player_y += 1

    elif action == "LEFT" and can_move(player_x - 1, player_y):
        player_x -= 1

    elif action == "RIGHT" and can_move(player_x + 1, player_y):
        player_x += 1

    # A checks the tiles around the player for a chest or enemy
    elif action == "A":
        chest_found = False

        positions = [
            (player_x, player_y - 1),
            (player_x, player_y + 1),
            (player_x - 1, player_y),
            (player_x + 1, player_y)
        ]

        # checks if any nearby tile is a chest
        for x, y in positions:
            if 0 <= x < 10 and 0 <= y < 10:
                if game_map[y][x] == 2:
                    game_map[y][x] = 0
                    inventory.append("Potion")
                    chest_found = True
                    break

        # if there is no chest nearby it checks for an enemy
        if not chest_found:
            start_battle()

    # B opens the inventory menu
    elif action == "B":
        menu_open = True
        menu_selection = 0


# main game loop constantly checks if a button is being pressed
# performs the action and redraws the screen after something changes
draw_map()

while True:
    pressed = None

    # checks each physical button to see if it is being pressed
    for name, pin in buttons.items():
        if pin.value() == 0:
            pressed = name
            break

    if pressed:
        handle_button(pressed)

        if player_hp <= 0:
            game_over()

        # redraws the correct screen depending on the current game state
        if menu_open:
            draw_menu()

        elif in_battle:
            draw_map()
            tft.fill_rect(20, 65, 200, 90, BLACK)
            tft.text("WILD SLIME!", 65, 75, RED)
            tft.text("SLIME HP: {}".format(enemy_hp), 45, 105, WHITE)
            tft.text("A: ATTACK  B: RUN", 30, 130, YELLOW)

        else:
            draw_map()

        # waits for the button to be released so it does not repeat the action
        while pin.value() == 0:
            time.sleep_ms(10)

        time.sleep_ms(120)

    time.sleep_ms(20)
