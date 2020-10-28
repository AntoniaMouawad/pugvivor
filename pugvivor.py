import arcade
import random
from flying_sprite import FlyingSprite
from sound_countrols import ControllableSound
from pug_sprite import PugSprite
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "PUGVIVOR"

SCALING_BANANA = 0.1
SCALING_BONE = 0.06
SCALING_PUG = 0.17
SCALING_PB_J = 0.2
SCALING_CLOUD = 0.8

FINAL_LEVEL = 3
REQUIRED_SCORE_PER_LEVEL = 10

INSTRUCTION_SCREEN = 0
GAME_RUNNING = 1
GAME_OVER = 2
GAME_COMPLETED = 3
FINAL = 4

PLAY_THEME = True
PLAY_SOUND_EFFECTS = True


class Pugvivor(arcade.Window):
    """
    Player starts on the left, bananas appear on the right
    Player can move anywhere, but not off screen
    Player has to eat the PB and J but avoid bananas
    """

    def __init__(self, width, height, title):
        """Initialize the game
        """
        super().__init__(width, height, title)

        # Set up the empty sprite lists
        self.current_state = INSTRUCTION_SCREEN
        self.main_theme = ControllableSound('sounds/main_theme.wav')
        self.level = 1

    def setup(self):
        """Get the game ready to play
        """
        # Set the background color
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.main_theme.play(volume=0.1, pan=0.5, flag=PLAY_THEME)
        # Set up the player
        self.player = PugSprite("images/pug.png", SCALING_PUG, self.height, self.width)
        self.player.center_y = self.height / 2
        self.player.left = 10
        self.all_sprites.append(self.player)
        self.paused = False

        # Schedule bananas and clouds
        self.schedule_all()
        self.set_mouse_visible(False)

        # Start at level 1
        self.level = 1

    def schedule_all(self):
        arcade.schedule(self.add_banana, 0.2 + (0.6 / math.sqrt(self.level)))
        arcade.schedule(self.add_pb_j, 0.3 + (0.6 / math.sqrt(self.level)))
        arcade.schedule(self.add_cloud, 3)

    def unschedule_all(self):
        arcade.unschedule(self.add_banana)
        arcade.unschedule(self.add_cloud)
        arcade.unschedule(self.add_pb_j)

    def reset(self):
        # Stop the music
        self.main_theme.stop()
        self.score = 0
        self.is_respawning = True
        self.lives_list = arcade.SpriteList()
        self.bananas_list = arcade.SpriteList()
        self.clouds_list = arcade.SpriteList()
        self.pb_j_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        # Unschedule so that it doesn't keep spawning new objs while in instruction or game over screen
        self.unschedule_all()
        self.lives = 3
        self.score = 0
        self.add_lives()

    def draw_game(self):
        """
        Draw all the sprites, along with the score and the lives.
        """
        # Draw all the sprites.
        self.all_sprites.draw()

        # Put the text on the screen.
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 20, 550, arcade.color.WHITE, 25, bold=True)
        life_text = "Lives: "
        arcade.draw_text(life_text, 485, 550, arcade.color.WHITE, 25, bold=True)
        if self.score % REQUIRED_SCORE_PER_LEVEL == 0 and self.score != 0:
            arcade.draw_text(f"Level {self.level}", 0, 300, arcade.color.WHITE, 50, width=SCREEN_WIDTH, align='center')

    def add_lives(self):
        current_pos = 550
        for _ in range(self.lives):
            life = FlyingSprite("images/bone.png", SCALING_BONE)
            life.center_x = current_pos + life.width
            life.center_y = SCREEN_HEIGHT - 30
            current_pos += life.width
            self.lives_list.append(life)
            self.all_sprites.append(life)

    def add_banana(self, delta_time: float, scale=SCALING_BANANA):
        """Adds a new enemy to the screen

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """

        # First, create the new banana sprite
        banana = FlyingSprite("images/banana.png", scale)

        # Set its position to a random height and off screen right
        banana.left = random.randint(self.width, self.width + 80)
        banana.top = random.randint(50, self.height - 50)

        # Set its speed to a random speed heading left
        lower_limit, upper_limit = self.get_limits()
        banana.velocity = (random.randint(lower_limit, upper_limit), 0)

        # Add it to the bananas list
        self.bananas_list.append(banana)
        self.all_sprites.append(banana)

    def add_cloud(self, delta_time: float):
        """Adds a new cloud to the screen

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """

        # First, create the new cloud sprite
        cloud = FlyingSprite("images/cloud.png", SCALING_CLOUD)

        # Set its position to a random height and off screen right
        cloud.left = random.randint(self.width, self.width + 80)
        cloud.top = random.randint(30, self.height - 30)

        # Set its speed to a random speed heading left
        cloud.velocity = (random.randint(-4, -2), 0)

        # Add it to the clouds list
        self.clouds_list.append(cloud)
        self.all_sprites.append(cloud)

    def get_limits(self):
        if self.level == 1:
            lower_limit = -10
            upper_limit = -5
        elif self.level == 2:
            lower_limit = -11
            upper_limit = -7
        elif self.level == 4:
            lower_limit = -12
            upper_limit = -8
        else:
            lower_limit = -13
            upper_limit = -8
        return lower_limit, upper_limit

    def add_pb_j(self, delta_time: float):
        pb_j = FlyingSprite("images/pb_j.png", SCALING_PB_J)

        # Set its position to a random height and off screen right
        pb_j.left = random.randint(self.width, self.width + 80)
        pb_j.top = random.randint(50, self.height - 50)

        # Set its speed to a random speed heading left
        lower, upper = self.get_limits()
        pb_j.velocity = (random.randint(lower, upper), 0)

        # Add it to the bananas list
        self.pb_j_list.append(pb_j)
        self.all_sprites.append(pb_j)

    def on_key_press(self, symbol, modifiers):
        """Handle user keyboard input
        Q: Quit the game
        P: Pause/Unpause the game
        I/J/K/L: Move Up, Left, Down, Right
        Arrows: Move Up, Left, Down, Right

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if symbol == arcade.key.Q:
            # Quit immediately
            arcade.close_window()

        if self.current_state == GAME_RUNNING:
            if symbol == arcade.key.P:
                self.paused = not self.paused
                if not self.paused:
                    self.schedule_all()

            if symbol == arcade.key.I or symbol == arcade.key.UP:
                self.player.change_y = 5

            if symbol == arcade.key.K or symbol == arcade.key.DOWN:
                self.player.change_y = -5

            if symbol == arcade.key.J or symbol == arcade.key.LEFT:
                self.player.change_x = -5

            if symbol == arcade.key.L or symbol == arcade.key.RIGHT:
                self.player.change_x = 5

    def on_key_release(self, symbol: int, modifiers: int):
        """Undo movement vectors when movement keys are released

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if self.current_state == GAME_RUNNING:
            if (
                    symbol == arcade.key.I
                    or symbol == arcade.key.K
                    or symbol == arcade.key.UP
                    or symbol == arcade.key.DOWN
            ):
                self.player.change_y = 0

            if (
                    symbol == arcade.key.J
                    or symbol == arcade.key.L
                    or symbol == arcade.key.LEFT
                    or symbol == arcade.key.RIGHT
            ):
                self.player.change_x = 0

    def draw_game_over(self):
        """
        Draw "Game over" across the screen.
        """
        output = "Game Over"
        arcade.draw_text(output, 0, self.height / 2, color=arcade.color.WHITE, font_size=60, width=SCREEN_WIDTH,
                         align='center')
        output = "Click to restart"
        arcade.draw_text(output, 0, 250, arcade.color.WHITE, 27, width=SCREEN_WIDTH, align='center')

    def draw_image_full_screen(self, image):
        image_texture = arcade.load_texture(image)
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.width, self.height,
                                            image_texture)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if self.current_state == INSTRUCTION_SCREEN:
            # Start the game
            ControllableSound('sounds/lets_do_it.wav').play(volume=0.4, pan=0.5, flag=PLAY_SOUND_EFFECTS)
            self.reset()
            self.setup()
            self.current_state = GAME_RUNNING

        elif self.current_state == GAME_COMPLETED:
            ControllableSound('sounds/i_the_shihua.wav').play(volume=0.4, pan=0.5, flag=PLAY_SOUND_EFFECTS)
            self.current_state = FINAL

        elif self.current_state == FINAL:
            self.current_state = INSTRUCTION_SCREEN

        elif self.current_state == GAME_OVER:
            self.reset()
            self.current_state = INSTRUCTION_SCREEN

    def update(self, delta_time: float):
        """Update the positions and statuses of all game objects
        If paused, do nothing

        Arguments:
            delta_time {float} -- Time since the last update
        """
        if self.current_state == GAME_RUNNING:
            if self.paused:
                self.unschedule_all()
                return

            if self.main_theme.is_complete():
                self.main_theme.play(0.1, 0.5, flag=PLAY_THEME)
            # Did you hit anything? If so, end the game
            if not self.player.respawning:
                banana_pug_collision = self.player.collides_with_list(self.bananas_list)
                if len(banana_pug_collision) > 0:
                    self.lose_life(banana_pug_collision)
                    if self.lives > 0:
                        self.player.respawning = 1
                    else:
                        self.current_state = GAME_OVER
                        self.set_mouse_visible(True)
                        ControllableSound(
                            ':resources:/sounds/gameover2.wav').play(
                            volume=0.1, pan=0.5, flag=PLAY_SOUND_EFFECTS)

            hit_list = self.player.collides_with_list(self.pb_j_list)
            self.increase_score(hit_list)
            # Update everything
            if self.level > FINAL_LEVEL:
                self.set_mouse_visible(True)
                self.current_state = GAME_COMPLETED
                ControllableSound("sounds/woohoo.wav").play(
                    volume=0.4, pan=0.5, flag=PLAY_SOUND_EFFECTS)
                self.reset()
            self.all_sprites.update()

    def increase_score(self, hit_list):
        for el in hit_list:
            el.kill()
            self.score += 1
            if self.score != 0 and self.score % REQUIRED_SCORE_PER_LEVEL == 0:
                self.increase_level()

    def increase_level(self):
        if self.level != FINAL_LEVEL:
            ControllableSound('sounds/nn_the_pug.wav').play(volume=0.4, pan=0.5, flag=PLAY_SOUND_EFFECTS)

        self.level += 1
        self.unschedule_all()
        self.schedule_all()

    def lose_life(self, banana_pug_collision):
        banana = banana_pug_collision[0]
        self.all_sprites.remove(banana)
        self.bananas_list.remove(banana)
        ControllableSound('sounds/but_shihua.wav').play(volume=0.4, pan=0.5, flag=PLAY_SOUND_EFFECTS)
        self.lives -= 1
        removed_life = self.lives_list.pop()
        self.all_sprites.remove(removed_life)

    def on_draw(self):
        """Draw all game objects
        """
        arcade.start_render()
        if self.current_state == INSTRUCTION_SCREEN:
            self.draw_image_full_screen('images/welcome_to_pugvivor.png')
        elif self.current_state == GAME_RUNNING:
            self.draw_game()
        elif self.current_state == GAME_COMPLETED:
            self.draw_image_full_screen('./images/pug_birthday.jpg')
        elif self.current_state == FINAL:
            self.draw_image_full_screen('./images/chihuahua.jpg')
        else:
            self.draw_game()
            self.draw_game_over()


if __name__ == "__main__":
    app = Pugvivor(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
