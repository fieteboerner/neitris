import os
import sys


class ThemeLoader(object):
    __instance = None
    themes = {}

    def __new__(cls, name):
        if not cls.__instance:
            cls._instance = super(ThemeLoader, cls).__new__(cls)

        return cls._instance.get(name)

    def get(self, theme):
        if theme not in self.themes.keys():
            print "load %s theme" % theme
            sys.path.append(os.path.join('.', 'themes', theme))
            tpl = __import__(theme + '_theme')

            self.themes[theme] = tpl.Theme(theme)

        return self.themes[theme]
