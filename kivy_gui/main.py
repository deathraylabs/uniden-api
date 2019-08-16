"""Learning to use Kivy GUI framework."""

from kivy.app import App
from kivy.uix.widget import Widget

# from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

# from kivy.uix.floatlayout import FloatLayout

# Obj..Prop.. allows us to reference id name in kv file
from kivy.properties import ObjectProperty, NumericProperty

# from kivy.uix.button import Button
# from kivy.uix.label import Label

from scanner.constants import *
from scanner.uniden import *


class BoxWindow(BoxLayout):
    """Is this object even necessary?"""

    pass


class DataWindow(Widget):
    """This is the main window for the app."""

    # todo: format label positions
    # todo: hook up button logic to get data for view

    # initialize id reference to kv file using variable name
    fav_list_name = ObjectProperty(None)
    sys_name = ObjectProperty(None)

    def btn(self):
        """Method runs when Button object calls root.btn() from <DataWindow>"""
        # print(f"favorites list: {self.fav_list_name.text}")
        print(f"size: {self.size}")
        print(f"label size: {self.height}")

        # this is how you change the text for labels defined in kv file
        # self.fav_list_name.text = "Hi there, dude!"
        # self.sys_name.text = "I updated too!"

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
        window.size
        return window


if __name__ == "__main__":
    DataWindowApp().run()
