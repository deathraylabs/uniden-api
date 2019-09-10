"""Learning to use Kivy GUI framework."""
import sys
import os
import pprint
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.config import Config

# from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen

# from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty  # ref name in kv file

if os.environ.get("TEXTDOMAIN") == "Linux-PAM":
    print("On RPi")
    sys.path.extend(["/home/pi/uniden-api", "/home/pi/uniden-api/scanner"])

print("Checked if on RPi")

from scanner.uniden import UnidenScanner

# from scanner.scanner_utility_functions import get_wav_meta
# from scanner.constants import GSI_OUTPUT

Builder.load_file("datawindow_screens.kv")


class DataWindow(Screen):
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

    scan_status_button = ObjectProperty()

    # can I store the sound object here?
    sound = ObjectProperty()
    # initialize variable to store scanner data
    scanner = None  # trying this

    # time interval to refresh data
    refresh_data_dt = 0.1

    def __init__(self, **kwargs):
        super(DataWindow, self).__init__(**kwargs)

        # color for hold highlight
        self.highlight_color = (0.8, 0.8, 0, 0.8)
        self.transparent_color = (1, 1, 1, 0)

    def scanner_status_btn(self):
        """Start pulling scanner display data."""

        Logger.info("scanner status button was pressed")

        # Set the timer for redrawing the screen
        refresh_time = self.refresh_data_dt

        # check to see if scanner instance has been created
        if self.scanner is None:
            Logger.info("Scanner is not initialized.")

            Logger.info("Trying to initialize scanner...")
            self.scanner = UnidenScanner()
            Logger.info("Scanner is initialized. Checking port connection...")

        if not self.scanner.port_is_open():
            port_open = self.scanner.open()

            if not port_open:
                Logger.info(
                    "Cannot open port. Scanner is likely not connected to computer."
                )
                return False

        Logger.info("The scanner port is open.")

        Logger.info("clearing the buffer")
        self.scanner.reset_port()

        self.scan_status_button.text = "Pull Startup"

        # start the scanner push updates
        # self.scanner.start_push_updates(interval=250)

        # start the screen update process
        Clock.schedule_interval(self.update_screen, refresh_time)

        self.scan_status_button.text = "Pull Mode"
        self.scan_status_button.color = (1, 1, 1, 0.5)

    def scanner_disconnect_btn(self):
        """Closes connection to scanner."""

        # make sure the port is open and connected to scanner
        try:
            if not self.scanner.port_is_open():
                Logger.info("Port is already closed.")
                return False
        except AttributeError:
            Logger.exception("No scanner connection", exc_info=False)
            return False

        Logger.info("Disconnect button pushed.")
        # stop updating screen with clock
        Clock.unschedule(self.update_screen)

        try:
            # stop the scanner push updates
            self.scanner.stop_push_updates()
            Logger.info("Stop update command sent to scanner.")
        except AttributeError:
            Logger.exception(
                "No scanner instance available to disconnect.", exc_info=False
            )
            return False

        self.scanner.close()
        Logger.info("Scanner Connection Closed.")

        # update button label
        self.scan_status_button.text = "Mirron\nScanner"
        self.scan_status_button.color = (1, 1, 1, 1)

    def scanner_hold(self, hold_key):
        """Method to hold/release a given system, department, or channel.

        See Also:
            scanner.push_key method contains details regarding button press
            command names.

        Args:
            hold_key (str): key press command

        Returns:
            res (str): push_key response string
        """
        Logger.debug("trying to hold channel")

        if self.scanner is None:
            Logger.error("No connection to scanner.")
            return False

        Logger.debug(f"bytes waiting: {self.scanner.serial.in_waiting}")
        res = self.scanner.push_key("press", hold_key)
        Logger.debug(f"hold button response: {res}")
        Logger.debug(
            f"bytes waiting after push_key(): {self.scanner.serial.in_waiting}"
        )

        return res

    def site_hold(self):
        """Method to hold/release site."""
        Logger.debug("trying to hold channel")

        if self.scanner is None:
            Logger.error("No connection to scanner.")
            return False

        res1 = self.scanner.push_key("press", "func")

        res2 = self.scanner.push_key("press", "dept")
        Logger.debug(f"responses: {res1}, {res2}")

    def print_data(self):
        """Mainly just a debugging step. This method prints the contents of
        the scanner state variable."""

        try:
            self.scanner.port_is_open()
        except AttributeError:
            return

        print("\n\nNew data\n\n")

        scanner_state = self.scanner.get_scanner_state()

        for item in scanner_state.items():
            # print(item)
            width = 25
            k = item[0]
            v = item[1]

            print(f"{k:{width}} {v}")

    def update_screen(self, dt):
        """Handles updates.
        Args:
            dt: argument used internally by kivy

        Returns:
            None
        """
        # update the scanner state variable first
        wav_meta = self.scanner.update_scanner_state()

        try:
            trans_start = wav_meta["transmission_start"]
        except KeyError:
            # Logger.exception("No transmission start time", exc_info=False)
            trans_start = "---"

        # calculate starting time in seconds
        # trans_start_sec = int(trans_start[-4:-2]) * 60 + int(trans_start[-2])
        # print(trans_start_sec)

        try:
            trans_end = wav_meta["transmission_end:1"]
        except KeyError:
            # Logger.exception("No transmission end time.", exc_info=False)
            trans_end = "---"

        # update DataWindow with metadata
        self.fav_list_name.text = wav_meta["MonitorList"]["Name"]
        self.sys_name.text = wav_meta["System"]["Name"]
        self.dept_name.text = wav_meta["Department"]["Name"]
        # self.tgid_name.text = wav_meta["TGID:Name"]
        self.tgid_hld.text = wav_meta["TGID"]["Name"]
        self.site_name.text = wav_meta["Site"]["Name"]
        self.transmission_start.text = trans_start
        self.transmission_end.text = trans_end

        # todo: calculate elapsed time in seconds using datetime
        self.total_time.text = "placeholder"

        self.unit_ids.text = wav_meta["UnitID"]["U_Id"]
        self.unit_ids_name_tag.text = wav_meta["UnitID"]["Name"]

        # code to highlight held quantities
        if wav_meta["Department"]["Hold"] == "On":
            self.ids["dept_name"].background_color = self.highlight_color
        else:
            self.ids["dept_name"].background_color = self.transparent_color

        if wav_meta["System"]["Hold"] == "On":
            self.ids["sys_name"].background_color = self.highlight_color
        else:
            self.ids["sys_name"].background_color = self.transparent_color

        if wav_meta["TGID"]["Hold"] == "On":
            # self.ids["tgid_name"].highlight_color = self.highlight_color
            self.ids["tgid_hld"].background_color = self.highlight_color
            # self.ids["tgid_hold_btn"].text = "Holding"
        else:
            # self.ids["tgid_name"].highlight_color = self.transparent_color
            self.ids["tgid_hld"].background_color = self.transparent_color
            # self.ids["tgid_hold_btn"].text = "Channel\nHold"

        if wav_meta["Site"]["Hold"] == "On":
            self.ids["site_name"].background_color = self.highlight_color
        else:
            self.ids["site_name"].background_color = self.transparent_color

        return


class PlaybackScreen(Screen):
    """Screen to contain playback controls."""

    play_stop_button = ObjectProperty()
    text_display = ObjectProperty()
    cmd_input_box = ObjectProperty()
    # can I store the sound object here?
    sound = ObjectProperty()
    scanner = None

    def btn(self):
        """Method runs when Button object calls root.btn() 
        from <DataWindow>"""
        pass
        #
        # wav_meta = get_wav_meta(wav_dir_path)
        #
        # # update the display
        # self.update_screen(wav_meta)
        # Logger.debug("Updated screen with WAV metadata.")
        #
        # return

    def play_stop_btn(self):
        """Button used to both play and stop sound playing from wav file on
        scanner. Currently disabled.
        """
        pass
        # filepath = wav_dir_path
        #
        # if self.sound is None:
        #     self.sound = SoundLoader.load(filepath)
        #     self.sound.play()
        #     self.play_stop_button.text = "STOP"
        # elif self.sound and self.sound.state == "play":
        #     position = self.sound.get_pos()
        #     print(position)
        #     self.sound.stop()
        #     self.play_stop_button.text = "PLAY"
        # else:
        #     print("Sound found at %s" % sound.source)
        #     print("Sound is %.3f seconds" % sound.length)
        #     self.sound.play()
        #     self.play_stop_button.text = "STOP"

    def stop_btn(self):
        """Button used to stop playback of sound. Currently disabled
        """
        pass
        # if self.sound:
        #     self.sound.stop()
        #     self.play_stop_button.text = "PLAY"

    def scanner_status_btn(self):
        """Start pulling scanner display data."""

        Logger.info("scanner status button was pressed")

        # check to see if scanner instance has been created
        if self.scanner is None:
            Logger.info("Scanner is not initialized.")

            Logger.info("Trying to initialize scanner...")
            self.scanner = UnidenScanner()
            Logger.info("Scanner is initialized. Checking port connection...")

        if not self.scanner.port_is_open():
            port_open = self.scanner.open()

            if not port_open:
                Logger.info(
                    "Cannot open port. Scanner is likely not connected to computer."
                )
                return False

        Logger.info("The scanner port is open.")

        Logger.info("clearing the buffer")
        self.scanner.reset_port()

    def scanner_disconnect_btn(self):
        """Button used to close the port used by scanner."""

        # make sure the port is open and connected to scanner
        try:
            if not self.scanner.port_is_open():
                Logger.info("Port is already closed.")
                return False
        except AttributeError:
            Logger.exception("No scanner connection", exc_info=False)
            return False

        Logger.info("Disconnect button pushed.")

        self.scanner.close()
        Logger.info("Scanner Connection Closed.")

    # todo: how can I share the scanner connection between pages?
    def command_input(self, value):
        """Method used to send raw commands to scanner and view the raw
        output. Used for experimentation.
        """

        try:
            self.scanner.send_command(value.text)
        except AttributeError:
            Logger.exception("Scanner port isn't open.", exc_info=False)
            return
        res = self.scanner.get_response()

        # display text response from scanner but pretty it up a bit
        self.text_display.text = pprint.pformat(res, compact=True, width=100, indent=3)
        self.cmd_input_box.focus = True


# create the screen manager
sm = ScreenManager()
sm.add_widget(DataWindow(name="datawindow"))
sm.add_widget(PlaybackScreen(name="playback"))


class DataWindowApp(App):
    """App class is called 'DataWindow', which means the 'kv' file should
    have the same name. As long as it's in the same wav_source as the main.py
    file it will be loaded at the same time.

    All based on the `Kivy Tutorial`_

    .. _`Kivy Tutorial`: https://github.com/kivy/kivy/wiki/Setting-Up-Kivy
    -with-various-popular-IDE's#setting-up-kivy-with-pycharm-on-osx

    """

    def build(self):
        """Handles something..."""

        # uncomment to configure datawindow separately
        # Config.read("datawindow.ini")

        # window = DataWindow()
        # return window
        return sm


if __name__ == "__main__":

    # path to wav_source that contains the audio of interest
    # wav_dir_path = (
    #     "/Users/peej/dev/uniden scanner "
    #     "scripts/uniden-api/kivy_gui/2019-07-17_15-04-13.wav"
    # )

    Config.set("kivy", "log_level", "debug")

    # run the GUI
    DataWindowApp().run()
