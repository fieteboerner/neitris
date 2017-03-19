from neitris_data import *
import os
import pygame


class BaseTheme:
    # General
    name = ''

    # Bricks
    bricks = {}
    borderBrick = 7
    brickCount = 7
    brickWidth = IMGX

    backgroundColor = (0, 0, 0)
    textColor = (255, 255, 255)

    def get_bricks(self):
        if not len(self.bricks):
            self.load_bricks()
            self.load_powerups()

        return self.bricks

    def load_bricks(self):
        for i in range(self.brickCount):
            path = os.path.join(".", "themes", self.name, "brick%d.png" % (i + 1))
            image = pygame.image.load(path)
            image = pygame.transform.scale(image, (self.brickWidth, self.brickWidth))
            self.bricks[i] = image

    def load_powerups(self):
        for p in powerups:
            if powerups[p].pid < POWERUP_MIN or powerups[p].pid > POWERUP_MAX:
                continue
            path = os.path.join(".", "powerups", "%s.png" % powerups[p].name)
            image = pygame.image.load(path)
            image = pygame.transform.scale(image, (self.brickWidth, self.brickWidth))
            self.bricks[powerups[p].pid - 1] = image

    def get_matrix_height(self):
        return YMAX * self.brickWidth

    def get_window_height(self):
        return self.get_matrix_height() + 135

    def get_matrix_width(self):
        return XMAX * self.brickWidth

    def get_window_width(self):
        return self.get_matrix_width() + 6 * self.brickWidth
