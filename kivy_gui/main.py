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

# from scanner.constants import *
# from scanner.uniden import *
from scanner.scanner_utility_functions import get_wav_meta


class BoxWindow(BoxLayout):
    """Is this object even necessary?"""

    pass


class DataWindow(Widget):
    """This is the main window for the app."""

    # todo: hook up button logic to get data for view

    # initialize id reference to kv file using variable name
    fav_list_name = ObjectProperty(None)
    sys_name = ObjectProperty(None)
    dept_name = ObjectProperty(None)
    site_name = ObjectProperty(None)
    unit_ids = ObjectProperty(None)
    unit_ids_name_tag = ObjectProperty(None)

    def btn(self):
        """Method runs when Button object calls root.btn() from <DataWindow>"""

        # see if the path is working
        print(wav_dir_path)

        wav_meta = get_wav_meta(wav_dir_path)

        # update DataWindow with metadata
        self.fav_list_name.text = wav_meta["FavoritesList:Name"]
        self.sys_name.text = wav_meta["System:Name"]
        self.dept_name.text = wav_meta["Department:Name"]
        self.site_name.text = wav_meta["Site:Name"]

        # unit ID information is not always present.
        try:
            self.unit_ids.text = wav_meta["UnitIds"]
        except KeyError as e:
            self.unit_ids.text = "-" * 8
            print("No UnitID data.")
        try:
            self.unit_ids_name_tag = wav_meta["UnitIds:NameTag"]
        except KeyError as e:
            self.unit_ids_name_tag.text = ""
            print(f"No Unit ID Name. {e}")

        # print(f"favorites list: {self.fav_list_name.text}")
        # print(f"size: {self.size}")
        # print(f"label size: {self.height}")

        # this is how you change the text for labels defined in kv file
        # self.fav_list_name.text = "Hi there, dude!"
        # self.sys_name.text = "I updated too!"

    def update(self, dt):
        """Handles updates."""
        pass


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
        # window.size
        return window


if __name__ == "__main__":
    # path to directory that contains the audio of interest
    wav_dir_path = "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-07-17_15-04-13.wav"

    # run the GUI
    DataWindowApp().run()
