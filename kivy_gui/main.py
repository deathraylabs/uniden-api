"""Learning to use Kivy GUI framework."""

from kivy.app import App
from kivy.config import Config
from kivy.logger import Logger, ColoredFormatter
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

# Obj..Prop.. allows us to reference id name in kv file
from kivy.properties import ObjectProperty

# from scanner.constants import *
# from scanner.uniden import *
from scanner.scanner_utility_functions import get_wav_meta
from scanner.uniden import runcmd, UnidenScanner, traverse_state

from pprint import pprint

from pathlib import Path


class BoxWindow(BoxLayout):
    """Is this object even necessary?"""

    pass


class DataWindow(Widget):
    """This is the main window for the app.

    Notes: creating an initialization method causes python to crash. I'm not
    sure why.
    """

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
    scan_status_button = ObjectProperty()

    # can I store the sound object here?
    sound = ObjectProperty()
    # initialize variable to store scanner data
    scanner = None

    def btn(self):
        """Method runs when Button object calls root.btn() from <DataWindow>"""

        wav_meta = get_wav_meta(wav_dir_path)

        # update the display
        self.update_screen(wav_meta)
        Logger.debug("Updated screen with WAV metadata.")

        return

    def play_stop_btn(self):

        filepath = wav_dir_path

        if self.sound is None:
            self.sound = SoundLoader.load(filepath)
            self.sound.play()
            self.play_stop_button.text = "STOP"
        elif self.sound and self.sound.state == "play":
            position = self.sound.get_pos()
            print(position)
            self.sound.stop()
            self.play_stop_button.text = "PLAY"
        else:
            # print("Sound found at %s" % sound.source)
            # print("Sound is %.3f seconds" % sound.length)
            self.sound.play()
            self.play_stop_button.text = "STOP"

    def stop_btn(self):
        if self.sound:
            self.sound.stop()
            self.play_stop_button.text = "PLAY"

    # todo: call update screen and pass data to it
    def scanner_status_btn(self):
        Logger.info("scanner status button press")

        try:
            port_is_open = self.scanner.port_is_open()
        except AttributeError:
            Logger.exception(
                "Scanner is not initialized, initializing " "now...", exc_info=False
            )
            # create scanner connection
            self.scanner = UnidenScanner()
            Logger.info("Scanner Connected.")

            self.scan_status_button.text = "Get XML"

            return

        if not self.scanner.port_is_open():
            self.scanner.open()
            self.scan_status_button.text = "Get XML"
            return

        Logger.debug("Running XML Method...")
        scanner_xml = runcmd(self.scanner)
        Logger.debug("XML method run successfully.")

        scanner_state = traverse_state(scanner_xml)
        Logger.debug(pprint(scanner_state))
        # pprint(scanner_state)

        self.update_screen(scanner_state)

    def scanner_disconnect_btn(self):
        try:
            self.scanner.close()
            Logger.debug("Scanner Connection Closed.")

            self.scan_status_button.text = "Connect to Scanner"
        except AttributeError:
            Logger.exception(
                "Scanner is not initialized, no port to close.", exc_info=False
            )

    def update_screen(self, updated_data):
        """Handles updates.
        Args:
            updated_data (dict): contains scanner data keys and values.

        Returns:
            None
        """
        wav_meta = updated_data

        try:
            trans_start = wav_meta["transmission_start"]
        except KeyError:
            Logger.exception("No transmission start time", exc_info=False)
            trans_start = "---"

        # calculate starting time in seconds
        # trans_start_sec = int(trans_start[-4:-2]) * 60 + int(trans_start[-2])
        # print(trans_start_sec)

        try:
            trans_end = wav_meta["transmission_end:1"]
        except KeyError:
            Logger.exception("No transmission end time.", exc_info=False)
            trans_end = "---"

        # update DataWindow with metadata
        self.fav_list_name.text = wav_meta["MonitorList:Name"]
        self.sys_name.text = wav_meta["System:Name"]
        self.dept_name.text = wav_meta["Department:Name"]
        self.site_name.text = wav_meta["Site:Name"]
        self.transmission_start.text = trans_start
        self.transmission_end.text = trans_end

        # todo: calculate elapsed time in seconds using datetime
        self.total_time.text = "placeholder"

        # unit ID information is not always present.
        try:
            self.unit_ids.text = wav_meta["UnitID:U_Id"]
        except KeyError:
            self.unit_ids.text = "-" * 8
            Logger.exception("UnitIds key doesn't exist", exc_info=False)
        try:
            self.unit_ids_name_tag.text = wav_meta["UnitID:Name"]
        except KeyError:
            self.unit_ids_name_tag.text = "-" * 8
            Logger.exception("No Unit ID Name.", exc_info=False)

        return


class DataWindowApp(App):
    """App class is called 'DataWindow', which means the 'kv' file should
    have the same name. As long as it's in the same wav_source as the main.py
    file it will be loaded at the same time.

    All based on the `Kivy Tutorial`_

    .. _`Kivy Tutorial`: https://github.com/kivy/kivy/wiki/Setting-Up-Kivy
    -with-various-popular-IDE's#setting-up-kivy-with-pycharm-on-osx

    """

    # def build_config(self, config):
    #     config.setdefaults("kivy", {"log_level": "info"})

    # def build_settings(self, settings):
    #     jsondata = (
    #         '[{"type": "title", '
    #         '"title": "My Application"},'
    #         '{"type": "options", "title": "my first key"}]'
    #     )
    #     settings.add_json_panel("My Application", self.config, data=jsondata)

    def build(self):
        """Handles something..."""

        # this allows us to configure this particular window in separate file
        Config.read("datawindow.ini")

        window = DataWindow()
        # window.size
        return window


if __name__ == "__main__":
    import sys
    import os

    if os.environ.get("TEXTDOMAIN") == "Linux-PAM":
        print("On RPi")
        sys.path.extend(["~/dev/uniden-api"])

    # path to wav_source that contains the audio of interest
    wav_dir_path = (
        "/Users/peej/dev/uniden scanner "
        "scripts/uniden-api/kivy_gui/2019-07-17_15-04-13.wav"
    )

    # wav_dir_path = (
    #     "/Users/peej/Downloads/uniden audio/-019-08-04_01-55-12/"
    #     "female wearing nothing.wav"
    # )

    # run the GUI
    DataWindowApp().run()
