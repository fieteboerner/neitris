import neitris_theme_base
import neitris_data
import os

SPECIAL_BORDER = neitris_data.POWERUP_MIN - 1


class Theme(neitris_theme_base.BaseTheme):

    bgColor = (138, 148, 108)
    matrixBgColor = (196, 207, 161)
    textColor = (65, 65, 65)
    gridColor = (177, 196, 160)

    borderBrick = SPECIAL_BORDER

    def load_special_bricks(self):
        path = os.path.join(".", "themes", self.name, "border.png")
        self.bricks[SPECIAL_BORDER-1] = self._get_image_by_path(path)