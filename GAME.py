'''
Author: Hanchen Wang
SID: 520374346
Unikey: hwan9127
Course: INFO1111 Computing 1A Professionalism
'''
# 20/3/2022 Scoreboard Bug: Scoreboard does not work a few pairs of barriers regularly when passing them.
# 26/3/2022 Fixed by changing the logic of counting from barrier_x passes player_x to removing the pair of barrier.
# 26/3/2022 Adjust the default position of character in game scene, so player has more time reacting to the upcoming
# barriers.
# 14/5/2022 Add quick restart keyboard 'R' to the game.
# 15/5/2022 Horizontal movement control is introduced to player.
# 16/5/2022 Add timer. Implement the random generation of barriers.
# 16/5/2022 Timer Bug: Do not reset to 0 after player loses the game.
# 17/5/2022 Fixed by changing the time-tracking method from assigning pygame.time.get.tick() to subtracting two phrases
# using time.time().
# 17/5/2022 Add flash skill and class Shadow.

import os
import random
import time

import pygame

'''Constants assignment'''
W, H = 288, 512  # Width and height of the program which is called repeatedly
FPS = 60  # Frames per second

'''Game setup'''
pygame.init()  # Initialize
SCREEN = pygame.display.set_mode((W, H))  # Set the size of program, which needs to be matched with the graphics
pygame.display.set_caption('Flappy Paimon')  # Name the window
CLOCK = pygame.time.Clock()  # Create a clock object which can be used to keep track of time

'''material import'''
IMAGES = {}  # Create an empty dictionary for the graphics file
for image in os.listdir('src/graphics'):  # List all src in this directory
    name, extension = os.path.splitext(image)  # Use Operating System to split the names and suffixes
    path = os.path.join('src/graphics', image)  # Import image file location for path
    IMAGES[name] = pygame.image.load(path)  # Define a method to load the image
GROUND_Y = H - IMAGES['ground'].get_height()  # To determine whether player falls to ground and loses the game
AUDIO = {}  # Same process for finding audio from the sounds file
for audio in os.listdir('src/sounds'):
    name, extension = os.path.splitext(audio)
    path = os.path.join('src/sounds', audio)
    AUDIO[name] = pygame.mixer.Sound(path)

'''Main scene functions definitions (main, begin, game, lose)'''


def main():
    global time_begin
    global time_start
    while True:
        AUDIO['An Interesting Labour'].play()  # Main background music
        AUDIO['PaimonSound3'].play()  # "Paimon da!" SE
        IMAGES['bgpic'] = IMAGES['sky']  # Unchanged background picture
        IMAGES['player'] = [IMAGES['player-up'],
                            IMAGES['player-mid'],
                            IMAGES['player-down']]  # Include player's three frames
        IMAGES['shadow'] = [IMAGES['shadow-up'], IMAGES['shadow-mid'], IMAGES['shadow-down']]
        barrier = IMAGES[
            random.choice(['barrier1', 'barrier2', 'barrier3'])]  # Choose one between three barriers each game
        IMAGES['barriers'] = [barrier,
                              pygame.transform.flip(barrier, False, True)]  # Store two inverted barriers in IMAGES[]
        begin()  # Call begin scene
        time_begin = time.time()  # Set default timer
        result = game()  # Call game scene
        lose(result)  # Call lose scene


# Begin scene
def begin():
    # Set the position of ground
    ground_gap = IMAGES['ground'].get_width() - W  # The width difference between two pictures
    ground_x = 0

    # Set the position of title graphic
    title_x = (W - IMAGES['title'].get_width()) / 2
    title_y = (GROUND_Y - IMAGES['title'].get_height()) / 2

    # Set the position, automatic moving range, moving velocity and animation frames of Paimon
    player_y = (H - IMAGES['player'][0].get_height()) / 2
    player_x = -50  # Chacracter begin outside the screen
    player_y_vel = 0.2  # Vertical moving
    player_x_vel = 2  # Horizontal moving
    player_y_range = [player_y - 5, player_y + 5]
    player_x_range = [-50, W]
    animation = 0
    frames = [0] * 20 + [1] * 10 + [2] * 20 + [1] * 10  # Slow the motion by multiplying frames

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()  # Register all events from the user into an event queue which can be received by Pygame
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return  # Only when SPACE is pressed changed to game scene
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # When R is pressed, restart game
                AUDIO['An Interesting Labour'].stop()
                AUDIO['PaimonSound3'].stop()
                AUDIO['PaimonSound2'].stop()
                AUDIO['PaimonSound1'].stop()
                AUDIO['Crash'].stop()
                AUDIO['Fly'].stop()
                main()

        ground_x -= 3  # Make the ground move
        if ground_x <= - ground_gap:  # When the ground goes to out of screen
            ground_x = 0  # Reset the position of ground to 0

        player_y += player_y_vel
        player_x += player_x_vel
        if player_y < player_y_range[0] or player_y > player_y_range[1]:
            player_y_vel *= -1  # Reverse the direction of motion when character out of range
        if player_x > player_x_range[1]:
            player_x = player_x_range[0]

        animation += 1  # Increase the id of sprites
        animation %= len(frames)  # The reminder will always be in id 1-19

        # Neccessary for these graphics to appear on the screen
        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        SCREEN.blit(IMAGES['ground'], (ground_x, GROUND_Y))
        SCREEN.blit(IMAGES['title'], (title_x, title_y))
        SCREEN.blit(IMAGES['player'][frames[animation]], (player_x, player_y))
        pygame.display.update()  # Continously update the displayed screen
        CLOCK.tick(FPS)  # Control frame rate


# Play scene
def game():
    AUDIO['Fly'].play()  # Play SE
    score = 0  # Set default scoreboard
    ground_gap = IMAGES['ground'].get_width() - W
    ground_x = 0
    player = Player(W * 0.2, H * 0.4)  # Assign the default position of character/player
    shadow = Shadow(W * (0.2 + 0.4), H * 0.4)  # Shadow is placed 0.4 screen width in front of player
    pairs = 10  # Number of barriers created once
    barrier_group = pygame.sprite.Group()  # Allow the collision detection by holding numerous sprite objects

    for i in range(pairs):  # An iteration for creating pairs of barriers with ranged location and length
        distance = random.randint(100, 250)  # A random distance between horizontal barriers each generation
        barrier_gap = random.randint(100, 200)  # A random gap between vertical barriers each generation
        barrier_y = random.randint(int(H * 0.4), int(H * 0.6))
        barrier_up = Barrier(W + i * distance, barrier_y, True)
        barrier_down = Barrier(W + i * distance, barrier_y - barrier_gap, False)
        barrier_group.add(barrier_up)
        barrier_group.add(barrier_down)

    while True:
        time_start = time.time()  # Set current timer
        seconds = int(time_start - time_begin)  # The difference is the seconds passed
        fly = False  # Default status is False, class player reacts if fly becomes True.
        forward = False  # Default status of player
        backward = False  # Default status of player

        for event in pygame.event.get():  # Player's control with keyboard
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # When SPACE is pressed, character moves up
                    fly = True
                    AUDIO['Fly'].stop()  # Avoid double audio play at the same time
                    AUDIO['Fly'].play()  # Play SE
                elif event.key == pygame.K_UP:  # Provides another choice to move up
                    fly = True
                    AUDIO['Fly'].stop()
                    AUDIO['Fly'].play()  # Play SE
                elif event.key == pygame.K_RIGHT:  # When -> is pressed, character moves right
                    forward = True
                elif event.key == pygame.K_LEFT:  # When <- is pressed, character moves left
                    backward = True
                elif event.key == pygame.K_DOWN:  # character stops horizontal movement
                    forward = False
                    backward = False
                    player.x_vel = 0  # Reset horizontal velocity of player
                    shadow.x_vel = 0  # Reset horizontal velocity of shadow
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    AUDIO['Flash'].play()  # Flash a distance and go through barriers
                    player.rect.x += W * 0.4  # Make both teleport a distance forward
                    shadow.rect.x += W * 0.4

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # Quick restart
                    AUDIO['An Interesting Labour'].stop()
                    AUDIO['PaimonSound3'].stop()
                    AUDIO['PaimonSound2'].stop()
                    AUDIO['PaimonSound1'].stop()
                    AUDIO['Crash'].stop()
                    AUDIO['Fly'].stop()
                    main()
        player.update(fly, forward, backward)
        shadow.update(fly, forward, backward)

        ground_x -= 3
        if ground_x <= - ground_gap:
            ground_x = 0

        first_barrier_up = barrier_group.sprites()[0]
        first_barrier_down = barrier_group.sprites()[1]
        if first_barrier_up.rect.right < 0:  # Destroy old barriers and create new ones
            barrier_y = random.randint(int(H * 0.4), int(H * 0.6))  # random height range
            barrier_gap = random.randint(100, 200)  # A random gap between vertical barriers each generation
            new_barrier_up = Barrier(first_barrier_up.rect.x + pairs * distance, barrier_y,
                                     True)  # Set position of up barrier
            new_barrier_down = Barrier(first_barrier_up.rect.x + pairs * distance, barrier_y - barrier_gap,
                                       False)  # Set position of down barrier
            barrier_group.add(new_barrier_up)
            barrier_group.add(new_barrier_down)
            first_barrier_up.kill()  # Remove up barrier
            first_barrier_down.kill()  # Remove down barrier
            score += 99  # Scoreboard increases as one pair of barriers leaves the screen
            AUDIO['PaimonSound2'].play()  # "Ehe" SE
        barrier_group.update()

        # Four ways to lose: Under the ground, above the top, touch left/right edge and collide with barriers
        if player.rect.y > GROUND_Y or player.rect.y < 0 or player.rect.x < 0 or player.rect.x > W \
                or pygame.sprite.spritecollideany(player, barrier_group):
            player.dying = True  # The dying process is activated
            AUDIO['Crash'].play()  # Play SE
            AUDIO['PaimonSound2'].stop()  # Stop the score SE first
            AUDIO['PaimonSound1'].play()  # Then play "Nan da yo" SE
            result = {'player': player, 'barrier_group': barrier_group, 'score': score, 'seconds': seconds}
            return result  # End this scene

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        barrier_group.draw(SCREEN)
        SCREEN.blit(IMAGES['ground'], (ground_x, GROUND_Y))
        scoreboard(score)
        timer(seconds)
        SCREEN.blit(player.image, player.rect)
        SCREEN.blit(shadow.image, shadow.rect)
        pygame.display.update()  # Updates the entire Surface on the display
        CLOCK.tick(FPS)


# Final scene
def lose(result):
    # Set the position of graphic gameover
    gameover_x = (W - IMAGES['gameover'].get_width()) / 2
    gameover_y = (GROUND_Y - IMAGES['gameover'].get_height()) / 2

    # When losing, leave player and barriers in the screen
    player = result['player']
    barrier_group = result['barrier_group']
    # coin_group = result['coin_group']

    while True:
        if player.dying:  # Control the falling-down animation
            player.go_die()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return  # Only when SPACE is pressed changed to begin scene
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # Quick restart
                    AUDIO['An Interesting Labour'].stop()
                    AUDIO['PaimonSound3'].stop()
                    AUDIO['PaimonSound2'].stop()
                    AUDIO['PaimonSound1'].stop()
                    AUDIO['Crash'].stop()
                    AUDIO['Fly'].stop()
                    main()

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        barrier_group.draw(SCREEN)
        SCREEN.blit(IMAGES['ground'], (0, GROUND_Y))
        SCREEN.blit(IMAGES['gameover'], (gameover_x, gameover_y))
        scoreboard(result['score'])
        timer(result['seconds'])
        AUDIO['An Interesting Labour'].stop()
        SCREEN.blit(player.image, player.rect)
        pygame.display.update()  # Updates the entire Surface on the display
        CLOCK.tick(FPS)


# The scoreboard and timer shown in game and lose scene
def scoreboard(score):  # Top-right number
    score_str = str(score)
    n = len(score_str)
    w = IMAGES['0'].get_width() * 1.1
    x = W - n * w
    y = 0
    for number in score_str:
        SCREEN.blit(IMAGES[number], [x, y])
        x += w


def timer(seconds):  # Top-left number
    seconds_str = str(seconds)
    # n = len(seconds_str)
    w = IMAGES['0'].get_width() * 1.1
    x = 0
    y = 0
    for number in seconds_str:
        SCREEN.blit(IMAGES[number], [x, y])
        x += w


# Build against two main objects Player and Barrier (Object-oriented)
class Player:
    def __init__(self, x, y):
        self.frames = [0] * 5 + [1] * 5 + [2] * 5 + [1] * 5  # The sequence showing up,middle,down,middle of the graphic
        self.animation = 0
        self.images = IMAGES['player']
        self.image = self.images[self.frames[self.animation]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_vel = 0  # Initial horizontal velocity
        self.y_vel = -4  # Initial vertical velocity
        self.max_y_vel = 8  # Maximum vertical velocity
        self.gravity = 0.3  # Acceleration of gravity
        self.rotate = 45  # Default angle (Point right is 0)
        self.max_rotate = -20  # Lowest angle
        self.rotate_vel = -3  # Decreased angle each frame affected by gravity
        self.y_vel_after_fly = -5  # Veritcal velocity after flying
        self.x_vel_after_forward = 1  # Horizaontal velocity after moving forward
        self.x_vel_after_backward = -3  # Horizaontal velocity after moving backward
        self.rotate_after_fly = 45  # Angle after flying
        self.dying = False  # Assign not in dying animation

    def update(self, fly=False, forward=False,
               backward=False):  # Default fly, forward, backward as False, in game() change to True
        if fly:  # Going up
            self.y_vel = self.y_vel_after_fly
            self.rotate = self.rotate_after_fly
        if forward:  # Going right
            self.x_vel = self.x_vel_after_forward
        if backward:  # Going left
            self.x_vel = self.x_vel_after_backward
        self.rect.x += self.x_vel
        # Velocity in the Y direction at any moment = the initial velocity (unchanged) + the acceleration of gravity
        # added to each frame
        self.y_vel = min(self.y_vel + self.gravity, self.max_y_vel)
        self.rect.y += self.y_vel
        # Rotate is equal to the original angle of the rotate+ frame rotate_vel
        self.rotate = max(self.rotate + self.rotate_vel, self.max_rotate)

        self.animation += 1
        self.animation %= len(self.frames)
        self.image = self.images[self.frames[self.animation]]
        # pygame.transform.rotate(surface, Angle) represent positions and rotation angles.
        self.image = pygame.transform.rotate(self.image, self.rotate)

    def go_die(self):  # When character becomes lowers than ground height
        if self.rect.y < GROUND_Y:
            self.rect.y += self.max_y_vel
            self.rotate = -90
            self.image = self.images[self.frames[self.animation]]
            self.image = pygame.transform.rotate(self.image, self.rotate)
        else:
            self.dying = False


class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, upwards=True):  # One pair of barriers contain upwards and downwards
        pygame.sprite.Sprite.__init__(self)
        if upwards:
            self.image = IMAGES['barriers'][0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = IMAGES['barriers'][1]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -3  # The velocity for barriers to move to left

    def update(self):
        self.rect.x += self.x_vel


'''
class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y, activate = False):
        pygame.sprite.Sprite.__init__(self)
        if activate:
            self.x_vel = 0
            self.image = IMAGES['shield'] #Shield appear on player
            self.rect.x = player.rect.x
            self.rect.y = player.rect.y
        else:
            self.image = IMAGES['coin'] #coin appear randomly in screen
            self.x_vel = -1
            self.rect.x = x
            self.rect.y = y

    def update(self):
        self.rect.x += self.x_vel
'''


class Shadow:  # Act as a destination indicator of player's flash skill
    def __init__(self, x, y):
        self.frames = [0] * 5 + [1] * 5 + [2] * 5 + [1] * 5  # The sequence showing up,middle,down,middle of the graphic
        self.animation = 0
        self.images = IMAGES['shadow']
        self.image = self.images[self.frames[self.animation]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_vel = 0  # Initial horizontal velocity
        self.y_vel = -4  # Initial vertical velocity
        self.max_y_vel = 8  # Maximum vertical velocity
        self.gravity = 0.3  # Acceleration of gravity
        self.rotate = 45  # Default angle (Point right is 0)
        self.max_rotate = -20  # Lowest angle
        self.rotate_vel = -3  # Decreased angle each frame affected by gravity
        self.y_vel_after_fly = -5  # Veritcal velocity after flying
        self.x_vel_after_forward = 1  # Horizaontal velocity after moving forward
        self.x_vel_after_backward = -3  # Horizaontal velocity after moving backward
        self.rotate_after_fly = 45  # Angle after flying
        self.dying = False  # Assign not in dying animation

    def update(self, fly=False, forward=False,
               backward=False):  # Default fly, forward, backward as False, in game() change to True
        if fly:  # Going up
            self.y_vel = self.y_vel_after_fly
            self.rotate = self.rotate_after_fly
        if forward:  # Going right
            self.x_vel = self.x_vel_after_forward
        if backward:  # Going left
            self.x_vel = self.x_vel_after_backward
        self.rect.x += self.x_vel
        # Velocity in the Y direction at any moment = the initial velocity (unchanged) + the acceleration of gravity
        # added to each frame
        self.y_vel = min(self.y_vel + self.gravity, self.max_y_vel)
        self.rect.y += self.y_vel
        # Rotate is equal to the original angle of the rotatation + frame rotate_vel
        self.rotate = max(self.rotate + self.rotate_vel, self.max_rotate)

        self.animation += 1
        self.animation %= len(self.frames)
        self.image = self.images[self.frames[self.animation]]
        # pygame.transform.rotate(surface, Angle) represent positions and rotation angles.
        self.image = pygame.transform.rotate(self.image, self.rotate)


if __name__ == "__main__":
    main()  # Call main() scene when the program run
