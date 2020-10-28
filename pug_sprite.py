from flying_sprite import FlyingSprite


class PugSprite(FlyingSprite):
    def __init__(self, filename: str = None, scale: float = 1, screen_height=800, screen_width=800):
        super().__init__(filename=filename, scale=scale)
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.respawning = 0
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new pug.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1

    def update(self):
        """Update the position of the sprite
        When it moves off screen to the left, remove it
        """

        # Move the sprite
        super().update()
        if self.respawning:
            self.respawning += 1
            if self.respawning > 20:
                self.respawning = 0

        # Keep the player on screen
        if self.top > self.screen_height:
            self.top = self.screen_height
        if self.right > self.screen_width:
            self.right = self.screen_width
        if self.bottom < 0:
            self.bottom = 0
        if self.left < 0:
            self.left = 0
