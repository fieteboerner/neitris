import neitris_theme_base
import neitris_data
import os

SPECIAL_BORDER = neitris_data.POWERUP_MIN - 1

class Theme(neitris_theme_base.BaseTheme):

    bgColor = (0, 0, 0)
    matrixBgColor = (92, 148, 252)
    textColor = (252, 188, 176)
    gridColor = (60, 188, 252)

    borderBrick = SPECIAL_BORDER

    def load_special_bricks(self):
        path = os.path.join(".", "themes", self.name, "border.png")
        self.bricks[SPECIAL_BORDER - 1] = self._get_image_by_path(path)
