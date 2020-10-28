import arcade


class ControllableSound(arcade.Sound):
    def __init__(self, sound_path):
        super().__init__(sound_path)

    def play(self, volume=1.0, pan=0.0, flag=True):
        super().play(volume=volume if flag else 0, pan=pan)
