"""Learning to use Kivy GUI framework."""
import sys
import os
import pprint
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty  # ref name in kv file
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.widget import Widget

from functools import partial  # ???

if os.environ.get("TEXTDOMAIN") == "Linux-PAM":
    print("On RPi")
    sys.path.extend(["/home/pi/uniden-api", "/home/pi/uniden-api/scanner"])

print("Checked if on RPi")

from scanner.uniden import UnidenScanner

# from scanner.scanner_utility_functions import get_wav_meta
# from scanner.constants import GSI_OUTPUT

# contains layout instructions for first screen
Builder.load_file("datawindow_screens.kv")
# contains layout instructions for playback screen
Builder.load_file("playback_screen.kv")
# contains formatting instructions for individual widgets
Builder.load_file("widget_formatting.kv")
# contains formatting instructions for the overlay screen
Builder.load_file("selection_overlay_screen.kv")


# class MyKeyboardListener(Widget):
#     def __init__(self, **kwargs):
#         super(MyKeyboardListener, self).__init__(**kwargs)
#         self._keyboard = Window.request_keyboard(self._keyboard_closed, self, "text")
#         if self._keyboard.widget:
#             # If it exists, this widget is a VKeyboard object which you can use
#             # to change the keyboard layout.
#             pass
#         self._keyboard.bind(on_key_down=self._on_keyboard_down)
#
#     def _keyboard_closed(self):
#         print("My keyboard have been closed!")
#         self._keyboard.unbind(on_key_down=self._on_keyboard_down)
#         self._keyboard = None
#
#     def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
#         print("The key", keycode, "have been pressed")
#         print(" - text is %r" % text)
#         print(" - modifiers are %r" % modifiers)
#
#         # Keycode is composed of an integer + a string
#         # If we hit escape, release the keyboard
#         if keycode[1] == "escape":
#             keyboard.release()
#
#         # Return True to accept the key. Otherwise, it will be used by
#         # the system.
#         return True


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
    command_input = ObjectProperty()

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

        # self.v_keyboard = MyKeyboardListener()

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

    def update_unid(self, value):
        """Update the unit ID text for the current unit ID."""

        print(f"unit ID name: {value.text}")

        self.scanner.set_unid_id_from_menu(value.text)

    def open_unid_menu(self):
        """experimental"""

        if self.scanner is None:
            Logger.error("scanner isn't connected")
            return False

        current_view = self.scanner.open_unid_set_menu()

        if isinstance(current_view, bool):
            Logger.error("You are not in menu state.")
            return False

        try:
            unid_name = current_view["Edit Name"]["Value"]
        except KeyError:
            Logger.exception("no unid name available.")
            return False

        self.command_input.text = unid_name

        return True

    def update_screen(self, dt):
        """Handles updates.
        Args:
            dt: argument used internally by kivy

        Returns:
            None
        """
        # update the scanner state variable first
        wav_meta = self.scanner.update_scanner_state()

        if isinstance(wav_meta, bool):
            Logger.error("No data returned by scanner.")
            return False

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
        # self.text_display.height = self.text_display.texture_size[1]
        # self.cmd_input_box.focus = True


class SelectionOverlayScreen(Screen):
    """This class handles scanner events that cause an overlay screen to appear.
    Overlay screens have to be handled before the scanner returns to normal operation
    and usually involve a Y/N response.
    """

    pass


# class ModeScreen(Screen):
#     """
#     Present the option to change keyboard mode and warn of system-wide
#     consequences.
#
#     Examples:
#         based on [https://github.com/kivy/kivy/blob/master/examples/keyboard/main.py][]
#     """
#
#     center_label = ObjectProperty()
#     mode_spinner = ObjectProperty()
#
#     keyboard_mode = ""
#
#     def on_pre_enter(self, *args):
#         """ Detect the current keyboard mode and set the text of the main
#         label accordingly. """
#
#         self.keyboard_mode = Config.get("kivy", "keyboard_mode")
#         self.mode_spinner.text = "'{0}'".format(self.keyboard_mode)
#
#         p1 = "Current keyboard mode: '{0}'\n\n".format(self.keyboard_mode)
#         if self.keyboard_mode in ["dock", "system", "systemanddock"]:
#             p2 = "You have the right setting to use this demo.\n\n"
#         else:
#             p2 = (
#                 "You need the keyboard mode to 'dock', 'system' or '"
#                 "'systemanddock'(below)\n in order to "
#                 "use custom onscreen keyboards.\n\n"
#             )
#
#         p3 = (
#             "[b][color=#ff0000]Warning:[/color][/b] This is a system-wide "
#             "setting and will affect all Kivy apps. If you change the\n"
#             " keyboard mode, please use this app"
#             " to reset this value to its original one."
#         )
#
#         self.center_label.text = "".join([p1, p2, p3])
#
#     def set_mode(self, mode):
#         """ Sets the keyboard mode to the one specified """
#         Config.set("kivy", "keyboard_mode", mode.replace("'", ""))
#         Config.write()
#         self.center_label.text = (
#             "Please restart the application for this\n" "setting to take effect."
#         )
#
#     def next(self):
#         """ Continue to the main screen """
#         self.manager.current = "keyboard"


# class KeyboardScreen(Screen):
#     """
#     Screen containing all the available keyboard layouts. Clicking the buttons
#     switches to these layouts.
#     """
#
#     display_label = ObjectProperty()
#     kb_container = ObjectProperty()
#
#     def __init__(self, **kwargs):
#         super(KeyboardScreen, self).__init__(**kwargs)
#         self._add_keyboards()
#         self._keyboard = None
#
#     def _add_keyboards(self):
#         """ Add a buttons for each available keyboard layout. When clicked,
#         the buttons will change the keyboard layout to the one selected. """
#         layouts = list(VKeyboard().available_layouts.keys())
#         # Add the file in our app directory, the .json extension is required.
#         layouts.append("numeric.json")
#         for key in layouts:
#             self.kb_container.add_widget(
#                 Button(text=key, on_release=partial(self.set_layout, key))
#             )
#
#     def set_layout(self, layout, button):
#         """ Change the keyboard layout to the one specified by *layout*. """
#         kb = Window.request_keyboard(self._keyboard_close, self)
#         if kb.widget:
#             # If the current configuration supports Virtual Keyboards, this
#             # widget will be a kivy.uix.vkeyboard.VKeyboard instance.
#             self._keyboard = kb.widget
#             self._keyboard.layout = layout
#         else:
#             self._keyboard = kb
#
#         self._keyboard.bind(on_key_down=self.key_down, on_key_up=self.key_up)
#
#     def _keyboard_close(self, *args):
#         """ The active keyboard is being closed. """
#         if self._keyboard:
#             self._keyboard.unbind(on_key_down=self.key_down)
#             self._keyboard.unbind(on_key_up=self.key_up)
#             self._keyboard = None
#
#     def key_down(self, keyboard, keycode, text, modifiers):
#         """ The callback function that catches keyboard events. """
#         self.display_label.text = "Key pressed - {0}".format(text)
#
#     # def key_up(self, keyboard, keycode):
#     def key_up(self, keyboard, keycode, *args):
#         """ The callback function that catches keyboard events. """
#         # system keyboard keycode: (122, 'z')
#         # dock keyboard keycode: 'z'
#         if isinstance(keycode, tuple):
#             keycode = keycode[1]
#         self.display_label.text += " (up {0})".format(keycode)


class DataWindowApp(App):
    """App class is called 'DataWindow', which means the 'kv' file should
    have the same name. As long as it's in the same wav_source as the main.py
    file it will be loaded at the same time.

    All based on the `Kivy Tutorial`_

    .. _`Kivy Tutorial`: https://github.com/kivy/kivy/wiki/Setting-Up-Kivy
    -with-various-popular-IDE's#setting-up-kivy-with-pycharm-on-osx

    """

    sm = None  # the root screen manager

    def build(self):
        """Handles something..."""

        # uncomment to configure datawindow separately
        # Config.read("datawindow.ini")

        # create the screen manager
        self.sm = ScreenManager()
        self.sm.add_widget(DataWindow(name="datawindow"))
        self.sm.add_widget(PlaybackScreen(name="playback"))
        # self.sm.add_widget(ModeScreen(name="mode"))
        # self.sm.add_widget(KeyboardScreen(name="keyboard"))
        # self.sm.current = "mode"

        return self.sm


if __name__ == "__main__":

    # path to wav_source that contains the audio of interest
    # wav_dir_path = (
    #     "/Users/peej/dev/uniden scanner "
    #     "scripts/uniden-api/kivy_gui/2019-07-17_15-04-13.wav"
    # )

    Config.set("kivy", "log_level", "debug")

    # run the GUI
    DataWindowApp().run()
