"""Learning to use Kivy GUI framework."""

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

# from kivy.uix.button import Button
# from kivy.uix.label import Label

# Obj..Prop.. allows us to reference id name in kv file
from kivy.properties import ObjectProperty

# from scanner.constants import *
# from scanner.uniden import *
from scanner.scanner_utility_functions import get_wav_meta
from pathlib import Path


class BoxWindow(BoxLayout):
    """Is this object even necessary?"""

    pass


class DataWindow(Widget):
    """This is the main window for the app."""

    # todo: hook up button logic to get data for view

    # initialize id reference to kv file using variable name
    fav_list_name = ObjectProperty()
    sys_name = ObjectProperty()
    dept_name = ObjectProperty()
    site_name = ObjectProperty()
    unit_ids = ObjectProperty()
    unit_ids_name_tag = ObjectProperty()
    transmission_start = ObjectProperty()
    transmission_end = ObjectProperty()
    total_time = ObjectProperty()
    play_stop_button = ObjectProperty()

    # can I store the sound object here?
    sound = ObjectProperty()

    def btn(self):
        """Method runs when Button object calls root.btn() from <DataWindow>"""

        # see if the path is working
        # print(wav_dir_path)

        wav_meta = get_wav_meta(wav_dir_path)

        trans_start = wav_meta["transmission_start"]

        # calculate starting time in seconds
        # trans_start_sec = int(trans_start[-4:-2]) * 60 + int(trans_start[-2])
        # print(trans_start_sec)

        trans_end = wav_meta["transmission_end:1"]

        # update DataWindow with metadata
        self.fav_list_name.text = wav_meta["FavoritesList:Name"]
        self.sys_name.text = wav_meta["System:Name"]
        self.dept_name.text = wav_meta["Department:Name"]
        self.site_name.text = wav_meta["Site:Name"]
        self.transmission_start.text = trans_start
        self.transmission_end.text = trans_end

        # todo: calculate elapsed time in seconds using datetime
        self.total_time.text = "placeholder"

        # unit ID information is not always present.
        try:
            self.unit_ids.text = wav_meta["UnitIds"]
        except KeyError:
            self.unit_ids.text = "-" * 8
            print("No UnitID data.")
        try:
            self.unit_ids_name_tag = wav_meta["UnitIds:NameTag"]
        except KeyError:
            self.unit_ids_name_tag.text = ""
            print(f"No Unit ID Name.")

        # print(f"favorites list: {self.fav_list_name.text}")
        # print(f"size: {self.size}")
        # print(f"label size: {self.height}")

        # this is how you change the text for labels defined in kv file
        # self.fav_list_name.text = "Hi there, dude!"
        # self.sys_name.text = "I updated too!"

    def play_stop_btn(self):

        filepath = wav_dir_path

        if self.sound is None:
            self.sound = SoundLoader.load(filepath)
            self.sound.play()
        elif self.sound and self.sound.state == "play":
            position = self.sound.get_pos()
            print(position)
            self.sound.stop()
        else:
            # print("Sound found at %s" % sound.source)
            # print("Sound is %.3f seconds" % sound.length)
            self.sound.play()

    def stop_btn(self):
        if self.sound:
            self.sound.stop()

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
    wav_dir_path = (
        "/Users/peej/dev/uniden scanner "
        "scripts/uniden-api/kivy_gui/2019-07-17_15-04-13mus.wav"
    )

    # wav_dir_path = (
    #     "/Users/peej/Downloads/uniden audio/-019-08-04_01-55-12/"
    #     "female wearing nothing.wav"
    # )

    # run the GUI
    DataWindowApp().run()
