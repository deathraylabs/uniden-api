"""Learning to use Kivy GUI framework."""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

# from kivy.uix.button import Button
# from kivy.uix.label import Label

from scanner.constants import *
from scanner.uniden import *


class DataWindow(Widget):
    """Root element of Application UI."""

    dickbutt = ObjectProperty(None)

    def update(self, dt):
        """Handles updates."""
        pass

    # variable for testing
    zoop = UNID_FAVORITES_DATA


class DataWindowApp(App):
    """App class is called 'DataWindow', which means the 'kv' file should
    have the same name. As long as it's in the same directory as the main.py
    file it will be loaded at the same time.

    All based on the `Kivy Tutorial`_

    .. _`Kivy Tutorial`: https://github.com/kivy/kivy/wiki/Setting-Up-Kivy
    -with-various-popular-IDE's#setting-up-kivy-with-pycharm-on-osx

    """

    def build(self):
        """Handles something..."""
        window = DataWindow()
        return window


if __name__ == "__main__":
    DataWindowApp().run()
