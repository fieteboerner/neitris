from neitris_data import *
import os
import pygame


class BaseTheme:
    # General
    name = None

    # Bricks
    bricks = {}
    borderBrick = 7
    brickCount = 7
    brickWidth = IMGX

    # Style
    bgColor = (0, 0, 0)
    matrixBgColor = (0, 0, 0)
    textColor = (255, 255, 255)
    gridColor = (80, 80, 80)

    def __init__(self, name):
        self.name = name

    def get_bricks(self):
        if not len(self.bricks):
            self.load_bricks()
            self.load_special_bricks()
            self.load_powerups()

        return self.bricks

    def load_bricks(self):
        for i in range(self.brickCount):
            path = os.path.join(".", "themes", self.name, "brick%d.png" % (i + 1))
            self.bricks[i] = self._get_image_by_path(path)

    def load_special_bricks(self):
        pass

    def load_powerups(self):
        for p in powerups:
            if powerups[p].pid < POWERUP_MIN or powerups[p].pid > POWERUP_MAX:
                continue
            path = os.path.join(".", "powerups", "%s.png" % powerups[p].name)
            self.bricks[powerups[p].pid - 1] = self._get_image_by_path(path)

    def _get_image_by_path(self, path):
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (self.brickWidth, self.brickWidth))
        return image

    def get_matrix_height(self):
        return YMAX * self.brickWidth

    def get_window_height(self):
        return self.get_matrix_height() + 135

    def get_matrix_width(self):
        return XMAX * self.brickWidth

    def get_window_width(self):
        return self.get_matrix_width() + 7 * self.brickWidth
