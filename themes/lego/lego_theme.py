import neitris_theme_base
import neitris_data
import os

SPECIAL_BORDER = neitris_data.POWERUP_MIN - 1

class Theme(neitris_theme_base.BaseTheme):

    bgColor = (229, 229, 229)
    matrixBgColor = (16, 155, 9)
    textColor = (0, 0, 0)
    gridColor = (30, 165, 10)

    borderBrick = SPECIAL_BORDER

    def load_special_bricks(self):
        path = os.path.join(".", "themes", self.name, "border.png")
        self.bricks[SPECIAL_BORDER - 1] = self._get_image_by_path(path)
