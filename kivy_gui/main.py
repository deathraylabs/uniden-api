"""Learning to use Kivy GUI framework."""
import sys
import os
import pprint
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import *
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty  # ref name in kv file
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from functools import partial  # ???

if os.environ.get("TEXTDOMAIN") == "Linux-PAM":
    print("On RPi")
    sys.path.extend(["/home/pi/uniden-api", "/home/pi/uniden-api/scanner"])

print("Checked if on RPi")

from scanner.uniden import UnidenScanner

# contains layout instructions for first screen
Builder.load_file("datawindow_screen.kv")
# contains layout instructions for playback screen
Builder.load_file("playback_screen.kv")
# contains formatting instructions for individual widgets
Builder.load_file("widget_formatting.kv")
# contains formatting instructions for the popup screen
Builder.load_file("popup_screen.kv")


# class ScrollingTextDisplayPanel(Label):
#     pass


class ScannerConnection(UnidenScanner):
    """Object that handles communication with the scanner and is instantiated at the
    root level."""

    def __init__(self, **kwargs):
        # this should allow me access to the UnidenScanner methods directly from
        # an instance of this class
        super(ScannerConnection, self).__init__(**kwargs)

        self.s = UnidenScanner()  # will open a connection automatically

    def open_connection(self):
        """Handles connecting to the scanner should the connection need to be
        reestablished

        Returns:
            True: if the scanner port is open
            False: if the scanner port is unable to be opened
        """

        if not self.s.port_is_open():
            Logger.debug(f"open_connection: scanner port is not open")
            port_open = self.s.open()

            if not port_open:
                Logger.info(
                    "Cannot open port. Scanner is likely not connected to computer."
                )
                return False

        Logger.info("open_connection: The scanner port is open.")

        return True

    def close_connection(self):
        """Close connection if needed
        """

        # make sure the port is open and connected to scanner
        try:
            if not self.s.port_is_open():
                Logger.info("Port is already closed.")
                return False
        except AttributeError:
            Logger.exception("No scanner connection", exc_info=False)
            return False

        try:
            # stop the scanner push updates
            self.s.stop_push_updates()
            Logger.info("Stop update command sent to scanner.")
        except AttributeError:
            Logger.exception(
                "No scanner instance available to disconnect.", exc_info=False
            )
            return False

        self.s.close()
        Logger.info("Scanner Connection Closed.")


# create a connection to scanner instance
scanner = ScannerConnection()


class UpdateScreen:
    """Class used to handle distributing data to appropriate screen at a set
    refresh rate.

    """

    def __init__(self):
        # time interval to refresh screen data
        self.refresh_data_dt = 0.1

    def start_auto_refresh(self):
        """Begin automatically refreshing screen data"""

        Logger.info(f"Auto refresh screen every {self.refresh_data_dt} sec requested")

        # Set the timer for redrawing the screen
        refresh_time = self.refresh_data_dt

        if not scanner.port_is_open():
            port_open = scanner.open()

            if not port_open:
                Logger.info(
                    "Cannot open port. Scanner is likely not connected to computer."
                )
                return False

        Logger.info("The scanner port is open.")

        Logger.info("clearing the buffer")
        scanner.reset_port()

        # start the screen update process
        Clock.schedule_interval(self.update_screen, refresh_time)

    def stop_auto_refresh(self):
        """method to stop auto updating"""
        Logger.info("Disconnect button pushed.")

        # stop updating screen with clock
        Clock.unschedule(self.update_screen)

        # # make sure the port is open and connected to scanner
        # try:
        #     if not scanner.port_is_open():
        #         Logger.info("Port is already closed.")
        #         return False
        # except AttributeError:
        #     Logger.exception("No scanner connection", exc_info=False)
        #     return False
        #
        # scanner.close()
        # Logger.info("Scanner Connection Closed.")

    def update_screen(self, dt):
        """When called this method updates the internal scanner state and then
        dispatches data to the appropriate window handler.

        Notes:
            - dt is an internal variable used by kivy, not by my code
            - use this method to handle updating scanner state instead of grabbing state
                from other methods or classes. That will ensure the last state seen
                by user is the same data that you are working with.

        Args:
            dt: kivy passes interval data through this variable
        """

        # update the scanner state variable first
        wav_meta = scanner.update_scanner_state()

        # check to ensure data is present
        if isinstance(wav_meta, bool):
            Logger.error("No data returned by scanner.")
            return False

        # check for a popup screen
        popup_screen = wav_meta.get("PopupScreen")
        if popup_screen != {}:
            print(popup_screen)

        # determine if screen is a menu or scan screen
        scanner_info = wav_meta.get("ScannerInfo")
        mode = scanner_info.get("Mode")
        v_screen = scanner_info.get("V_Screen")

        # update the side button panel
        side_panel.update_rightsidepanel(wav_meta)

        # scanner mode can be "Trunk Scan" or "Trunk Scan Hold", so use v_screen here
        if v_screen == "trunk_scan":
            # switch to the main screen and update it
            Logger.debug("update_screen: calling datawindow class")
            # switch over to datawindow screen
            sm.current = "datawindow"
            Logger.debug("update screen: switched over to datawindow")
            # side_panel.update_rightsidepanel(wav_meta)
            sm.current_screen.update_datawindow_screen(wav_meta)
        elif mode == "Menu tree":
            # switch to the popup screen and update it
            Logger.debug("update_screen: calling popup class")
            sm.current = "popup"
            sm.current_screen.update_popup_screen(wav_meta)
        else:
            Logger.error(f"update_screen: unknown screen: {v_screen}")
            return False

        # update the right side panel
        side_panel.update_rightsidepanel(wav_meta)

        return True


# todo: fix setup to change unit id name
class RightSidePanel(BoxLayout):
    """Panel that contains the user interface buttons"""

    # initialize id reference to kv file using variable name
    # volume_level = ObjectProperty()
    command_input = ObjectProperty()
    scan_status_button = ObjectProperty()
    mute_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super(RightSidePanel, self).__init__(**kwargs)

        self.red_text_color = (1, 0, 0, 1)
        self.white_text_color = (1, 1, 1, 1)

        # variable to store last volume level before mute
        self.vol_last = 0

    def scanner_disp_start_btn(self):
        """Start pulling scanner display data."""

        Logger.info("scanner status button was pressed")

        # call the screen updater method of UpdateScreen()
        update_screen.start_auto_refresh()

        self.scan_status_button.text = "Pulling"
        # self.scan_status_button.color = (1, 1, 1, 0.5)
        self.scan_status_button.color = self.red_text_color

        return True

    def scanner_disp_stop_btn(self):
        """Stops the auto-refresh routine but connection is still maintained with
        the scanner"""

        update_screen.stop_auto_refresh()

        # update button label
        self.scan_status_button.text = "Start"
        self.scan_status_button.color = (1, 1, 1, 1)

        return True

    def keypad_press(self, keypad_key, keypad_mode="press"):
        """Method to pass keypad press command to scanner.

        Args:
            keypad_key (str): see scanner.push_key docstring
            keypad_mode (str): see scanner.push_key docstring. defaults to simple press

        Returns:
            True: if keypad press is successful
            False: if scanner returns an error code

        """

        # check for connection
        if scanner is None:
            Logger.error("No connection to scanner.")
            return False

        res = scanner.push_key(keypad_mode, keypad_key)

        if res == 0:
            Logger.error(
                f"Scanner responded with error code to keypad input {keypad_key}"
            )
            return False

        return True

    def change_vol(self, cmd):
        """raise or lower the volume

        Notes:
            - Passing an integer from 0 to 15 will change the volume to that level
                directly.
            - Passing "up", "down", or "mute" will change volume incrementally or to zero

        Args:
            cmd (str): "up", "down", "mute"
            cmd (int): value between 0-15

        """
        current_vol = scanner.get_volume()

        if current_vol is False:
            # no current volume is set
            return False

        if cmd == "up":
            scanner.set_volume(delta=1)
        elif cmd == "down":
            scanner.set_volume(delta=-1)
        elif cmd == "mute" and current_vol != "0":
            # save the current volume level before muting
            self.vol_last = current_vol
            scanner.set_volume(vol=0)
        # reset the previous volume level
        elif cmd == "mute" and current_vol == "0":
            scanner.set_volume(vol=self.vol_last)
        elif isinstance(cmd, int):
            scanner.set_volume(vol=cmd)
        else:
            Logger.error("invalid volume command")
            return False

        # this will "push" the volume knob to make volume graph disappear
        scanner.push_key(mode="press", key="vpush")

        return True

    def set_current_screen(self, screen):
        """Change the currently displayed screen"""

        sm.current = screen

        return True

    def update_rightsidepanel(self, wav_meta):
        """Method to handle updating the button states on right side panel.

        Args:
            wav_meta (dict): standard dict formatted according to constants.py
                GSI_OUTPUT_2

        Returns:
            True: if executed without issue
            False: if screen doesn't use the right window control
        """

        # get the currently active screen
        current_screen = sm.get_screen(sm.current)

        try:
            right_screen = current_screen.right_screen
        except AttributeError:
            Logger.exception("screen doesn't use standard right window")
            return False

        # change the text display of menu button
        if current_screen.name == "popup":
            right_screen.menu_btn.text = "back\n(menu)"

            # change system key label to current usage
            right_screen.sys_softkey.text = "Back to\nScan"

        # properties dict from scanner
        get_property = wav_meta["Property"]

        # set the mute button formatting
        vol = get_property["VOL"]
        if vol == "0":
            right_screen.mute_btn.color = self.red_text_color
        else:
            right_screen.mute_btn.color = self.white_text_color

        # change the function key display if it's active
        func_key = get_property["F"]
        if func_key == "On":
            right_screen._function_button.color = self.red_text_color
        else:
            right_screen._function_button.color = self.white_text_color

        return True


# todo: window doesn't display conventional frequency data correctly, freezes screen
class DataWindow(Screen):
    """Screen used to display scanner data while scanning.

    """

    # initialize id reference to kv file using variable name
    volume_level = ObjectProperty()
    command_input = ObjectProperty()
    scan_status_button = ObjectProperty()
    right_screen = ObjectProperty()
    # main_container = ObjectProperty()

    def __init__(self, **kwargs):
        super(DataWindow, self).__init__(**kwargs)

        self.red_text_color = (1, 0, 0, 1)
        self.white_text_color = (1, 1, 1, 1)

        # color for hold highlight
        self.highlight_color = (0.8, 0.8, 0, 0.8)
        self.transparent_color = (1, 1, 1, 0)

        self.default_text_color = (1, 1, 1, 1)
        self.permanent_avoid_color = (0.8, 0.8, 0.8, 0.9)

        # dict correlates scanner tags to variable names
        self.data_tags = {
            "MonitorList": "fav_list_name",
            "System": "sys_name",
            "Department": "dept_name",
            "TGID": "tgid_hld",
            "Site": "site_name",
        }

    def scanner_hold(self, hold_key):
        """Method to hold/release a given system, department, or channel.

        See Also:
            scanner.push_key method contains details regarding button press
            command names.

        Args:
            hold_key (str): key press command for specific scanner button

        Returns:
            res (str): push_key response string
        """
        Logger.debug("trying to hold channel")

        if scanner is None:
            Logger.error("No connection to scanner.")
            return False

        Logger.debug(f"bytes waiting: {scanner.serial.in_waiting}")
        res = scanner.push_key("press", hold_key)
        Logger.debug(f"hold button response: {res}")
        Logger.debug(f"bytes waiting after push_key(): {scanner.serial.in_waiting}")

        return res

    def site_hold(self):
        """Method to hold/release site."""
        Logger.debug("trying to hold channel")

        if scanner is None:
            Logger.error("No connection to scanner.")
            return False

        res1 = scanner.push_key("press", "func")

        res2 = scanner.push_key("press", "dept")
        Logger.debug(f"responses: {res1}, {res2}")

    def print_data(self):
        """Mainly just a debugging step. This method prints the contents of
        the scanner state variable."""

        try:
            scanner.port_is_open()
        except AttributeError:
            return

        print("\n\nNew data\n\n")

        scanner_state = scanner.get_scanner_state()

        for item in scanner_state.items():
            # print(item)
            width = 25
            k = item[0]
            v = item[1]

            print(f"{k:{width}} {v}")

    def update_unid(self, value):
        """Update the unit ID text for the current unit ID."""

        print(f"unit ID name: {value.text}")

        scanner.set_unid_id_from_menu(value.text)

    def open_unid_menu(self):
        """experimental"""

        if scanner is None:
            Logger.error("scanner isn't connected")
            return False

        current_view = scanner.open_unid_set_menu()

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

    # todo: update buttons in kv file for case when function button is pressed
    # todo: update method to allow keypad combinations to be passed
    def keypad_press(self, keypad_key, keypad_mode="press"):
        """Method to pass keypad press command to scanner.

        Args:
            keypad_key (str): see scanner.push_key docstring
            keypad_mode (str): see scanner.push_key docstring. defaults to simple press

        Returns:
            True: if keypad press is successful
            False: if scanner returns an error code

        """

        # check for connection
        if scanner is None:
            Logger.error("No connection to scanner.")
            return False

        res = scanner.push_key(keypad_mode, keypad_key)

        if res == 0:
            Logger.error(
                f"Scanner responded with error code to keypad input {keypad_key}"
            )
            return False

        return True

    # def change_vol(self, cmd):
    #     """raise or lower volume
    #
    #     Notes:
    #         - Passing an integer from 0 to 15 will change the volume to that level
    #             directly.
    #         - Passing "up", "down", or "mute" will change volume incrementally or to zero
    #
    #     Args:
    #         cmd (str): "up", "down", "mute"
    #         cmd (int): value between 0-15
    #
    #     """
    #     current_vol = scanner.get_volume()
    #
    #     if current_vol is False:
    #         # no current volume is set
    #         return False
    #
    #     if cmd == "up":
    #         scanner.set_volume(delta=1)
    #     elif cmd == "down":
    #         scanner.set_volume(delta=-1)
    #     elif cmd == "mute" and current_vol != "0":
    #         # save the current volume level before muting
    #         self.vol_last = current_vol
    #         scanner.set_volume(vol=0)
    #     # reset the previous volume level
    #     elif cmd == "mute" and current_vol == "0":
    #         scanner.set_volume(vol=self.vol_last)
    #     elif isinstance(cmd, int):
    #         scanner.set_volume(vol=cmd)
    #     else:
    #         Logger.error("invalid volume command")
    #         return False
    #
    #     # this will "push" the volume knob to make volume graph disappear
    #     scanner.push_key(mode="press", key="vpush")
    #
    #     return True

    def update_datawindow_screen(self, wav_meta):
        """Handles updates.
        Args:
            wav_meta (dict): metadata read from scanner

        Returns:
            True: if no errors
        """

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

        # update the DataWindow with metadata from scanner
        for item in self.data_tags.items():
            wav_meta_dict = wav_meta[item[0]]
            kivy_id = self.ids[item[1]]

            # populate screen text
            kivy_id.text = wav_meta_dict["Name"]

            # code to highlight held quantities
            if item[0] == "MonitorList":  # favorites can't be held
                continue
            elif wav_meta_dict["Hold"] == "On":
                kivy_id.background_color = self.highlight_color
            else:
                kivy_id.background_color = self.transparent_color

            # check to see if item is set to Avoid
            # three states allowed are "Avoid", "T-Avoid", or "Off"
            if wav_meta_dict["Avoid"] == "Avoid":
                kivy_id.strikethrough = True
                kivy_id.color = self.permanent_avoid_color
            elif wav_meta_dict["Avoid"] == "T-Avoid":
                kivy_id.strikethrough = True
                kivy_id.color = self.default_text_color
            else:
                kivy_id.strikethrough = False
                kivy_id.color = self.default_text_color

        self.transmission_start.text = trans_start
        self.transmission_end.text = trans_end

        # Property values provided by scanner
        property_dict = wav_meta["Property"]

        self.volume_level.text = f'vol: {property_dict["VOL"]}'

        self.unit_ids.text = wav_meta["UnitID"]["U_Id"]
        self.unit_ids_name_tag.text = wav_meta["UnitID"]["Name"]

        # get the scanner overwrite text
        overwrite = wav_meta["OverWrite"]["Text"]

        # if scanner provides overwrite text, display it over the tgid area
        if overwrite != "":
            self.tgid_hld.text = overwrite
            self.tgid_hld.color = (0.2, 1, 1, 0.8)

        self.voice.text = property_dict["Mute"]
        self.ids["_status"].text = property_dict["P25Status"]
        self.ids["_squelch"].text = f'SQL:{property_dict["SQL"]}'
        self.ids["_signal"].text = f'sig: {property_dict["Sig"]}'
        self.ids["_rec"].text = f'REC: {property_dict["Rec"]}'

        return True


class PopupScreen(Screen):
    """Used to display menu items and other information that pops up in the course
    of using a mode other than scanning.

    Notes:
        - [ ] needs a method to handle getting menu view information
    """

    # object properties automatically provide access to instances..
    # created in a kv file
    text_display_popup = ObjectProperty()
    # give the RightSidePanel updater access to this screen's instance
    right_screen = ObjectProperty()
    # menu_items = ObjectProperty()

    def __init__(self, **kwargs):
        super(PopupScreen, self).__init__(**kwargs)

    def update_popup_screen(self, wav_meta):
        """display menu data when scanner is in menu mode

        Notes:
            - [ ] need some way to interact with menu structure in this view
        """

        # container for scrolling display
        scrolling_container = self.text_display_popup

        # this is the container where we want to generate the labels
        # layout = self.menu_items

        menu_information = self.get_menu_view()

        menu_error = menu_information.get("MenuErrorMsg")

        # dict that contains information on menu and selection
        msi_dict = menu_information.get("MSI")

        # catch menu error message and display it
        if menu_error is not None:
            Logger.error(f"menu error message: {menu_error['Text']}")
            text_out = menu_error["Text"]
        # this gets us the currently selected item
        # make sure there is actually a menu item present
        elif msi_dict is not None:
            for k, v in msi_dict.items():
                menu_name = k

                # check the type of menu we're looking at
                menu_type = v["MenuType"]

                if menu_type == "TypeSelect":
                    selected_item = v["Selected"]
                    # dictionary of menu items
                    menu_items = menu_information["MenuItem"]

                    # process the menu selections with this method
                    text_out = self.menu_selector(
                        menu_name=menu_name,
                        selected_item=selected_item,
                        menu_items=menu_items,
                    )
                # handle numeric input types
                elif menu_type == "TypeInput":
                    text_out = f"{menu_name}\n\n"
                    text_out += f"value: {v['Value']}"
                else:
                    text_out = "No Menu Output"
        else:
            Logger.error("Unusual menu structure encountered")
            return False

        # reset the text size so it fits in window
        scrolling_container.text_size[1] = None

        # self.text_display_popup.text = pprint.pformat(
        #     menu_item_list, compact=True, width=100, indent=3
        # )
        self.text_display_popup.text = text_out
        self.text_display_popup.height = self.text_display_popup.texture_size[1]

    def menu_selector(self, menu_name, selected_item, menu_items):
        """Method to select a menu item."""

        # list the key values in order they were added
        menu_item_list = list(menu_items)

        # format the data so it makes sense to a human
        text_out = f"{menu_name}\n\n"
        for item in menu_item_list:
            item_index = menu_items[item]["Index"]
            # not all items will have a value
            item_value = menu_items[item].get("Value")
            if item_value is None:
                item_value = ""
            else:
                item_value = f"{item_value} :"

            if selected_item == item_index:
                text_out += f"---> {item_value} {item}\n"
            else:
                text_out += f"     {item_value} {item}\n"

        return text_out

    def get_menu_view(self):
        """Uses the uniden scanner api to request menu view information from the
        scanner.

        Returns:
            res (dict): scanner MSI response in dict format
        """

        res = scanner.get_menu_view()

        return res

    def keypad_press(self, keypad_key, keypad_mode="press"):
        """Method to pass keypad press command to scanner.

        Args:
            keypad_key (str): see scanner.push_key docstring
            keypad_mode (str): see scanner.push_key docstring. defaults to simple press

        Returns:
            True: if keypad press is successful
            False: if scanner returns an error code

        """

        # check for connection
        if scanner is None:
            Logger.error("No connection to scanner.")
            return False

        res = scanner.push_key(keypad_mode, keypad_key)

        if res == 0:
            Logger.error(
                f"Scanner responded with error code to keypad input {keypad_key}"
            )
            return False

        return True


class PlaybackScreen(Screen):
    """temporary debugging and experimentation screen"""

    text_display = ObjectProperty()
    cmd_input_box = ObjectProperty()

    def __init__(self, **kwargs):
        super(PlaybackScreen, self).__init__(**kwargs)

        # get the current keyboard layout
        layout = Config.get("kivy", "keyboard_layout")
        print(f"current keyboard layout: {layout}")
        Config.set("kivy", "keyboard_layout", "qwerty")
        layout = Config.get("kivy", "keyboard_layout")
        print(f"current keyboard layout: {layout}")

    def btn(self):
        """Method runs when Button object calls root.btn() 
        from <DataWindow>"""

        # debugging
        get_child_names(self.ids)

        left_display = self.ids["_large_text_layout"]

        print("\n\n")

        # debugging
        get_child_names(self.popup_window.ids)

        # self.popup_label.color = (1, 1, 1, 1)
        # with self.popup_label.canvas:
        #     Color(rgba=(1, 1, 1, 1))
        #     Rectangle(size=left_display.size, pos=(-20, 0))

    # def scanner_status_btn(self):
    #     """Start pulling scanner display data."""
    #
    #     Logger.info("scanner status button was pressed")
    #
    #     scanner.open_connection()
    #
    #     port_is_open = scanner.port_is_open()
    #
    #     if port_is_open:
    #         Logger.info("scanner.open_connection: The scanner port is open.")
    #     else:
    #         Logger.info("scanner_status_btn: The port is still closed.")
    #
    #     Logger.info("clearing the buffer")
    #     res = scanner.reset_port()
    #     Logger.info(f"port reset: {res}")

    # def scanner_disconnect_btn(self):
    #     """Button used to close the port used by scanner."""
    #
    #     Logger.info("Disconnect button pushed.")
    #
    #     scanner.close_connection()
    #     # Logger.info("Scanner Connection Closed.")

    def command_input(self, value):
        """Method used to send raw commands to scanner and view the raw
        output. Used for experimentation.
        """

        try:
            scanner.send_command(value.text)
        except AttributeError:
            Logger.exception("Scanner port isn't open.", exc_info=False)
            return
        res = scanner.get_response()

        # display text response from scanner but pretty it up a bit
        formatted_response = pprint.pformat(res, compact=True, width=100, indent=3)
        self.text_display.text = formatted_response

        # append formatted response to the log file
        log_output(formatted_response)

        # you must remove focus before you can cancel the selection handles
        self.cmd_input_box.focus = False
        self.cmd_input_box.cancel_selection()

        return formatted_response

    def display_raw_scanner_output(self, command):
        """method to view raw output from a command

        Args:
            command (str): uniden scanner command string

        """
        # remove focus on input box
        self.cmd_input_box.focus = False

        ack = scanner.send_command(command)
        Logger.debug(ack)

        res = scanner.get_response()

        # pprint.pprint(res)

        # format response with pretty print so it is more readable
        formatted_response = pprint.pformat(res, compact=True, width=100, indent=3)

        # print(f"formatted {command} response:\n\n{formatted_response}")

        # reset the text size so it fits properly in window
        self.text_display.text_size[1] = None

        # display text on left text panel
        self.text_display.text = formatted_response
        self.text_display.height = self.text_display.texture_size[1]

    def fav_qk_status(self):
        """Experimenting with new methods"""

        # get raw quick key status
        qk_status = scanner.get_fav_list_qk_status()
        # get the quick key list for favorites
        qk_list = scanner.get_list("favorites list")

        # merge to make human-readable dict
        hr_dict = scanner.get_human_readable_qk_status(qk_status, qk_list)
        Logger.info(pprint.pformat(hr_dict))

        return True

    # ---------- currently unused ---------- #

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


sm = ScreenManager(transition=NoTransition())
sm.add_widget(DataWindow(name="datawindow"))
sm.add_widget(PlaybackScreen(name="playback"))
sm.add_widget(PopupScreen(name="popup"))

# create update screen instance that other classes can access
update_screen = UpdateScreen()

side_panel = RightSidePanel()


def log_output(log_string):
    """Helper function to quickly save scanner output to file

    Returns
        True: if no errors thrown
    """

    log_path = "scanner_log.txt"

    with open(log_path, "a") as log_file:
        log_file.write(log_string)

    return True


class DataWindowApp(App):
    """App class is called 'DataWindow', which means the 'kv' file should
    have the same name. As long as it's in the same wav_source as the main.py
    file it will be loaded at the same time.

    All based on the `Kivy Tutorial`_

    .. _`Kivy Tutorial`: https://github.com/kivy/kivy/wiki/Setting-Up-Kivy
    -with-various-popular-IDE's#setting-up-kivy-with-pycharm-on-osx

    """

    # sm = None  # the root screen manager

    # print(f"kivy data: {App.user_data_dir}")

    def build(self):
        """Handles something..."""

        # uncomment to configure datawindow separately
        # Config.read("datawindow.ini")

        # create the screen manager
        # self.sm = ScreenManager(transition=NoTransition())
        # self.sm.add_widget(DataWindow(name="datawindow"))
        # self.sm.add_widget(PlaybackScreen(name="playback"))
        # self.sm.add_widget(PopupScreen(name="popup"))
        # self.sm.add_widget(KeyboardScreen(name="keyboard"))
        # self.sm.current = "playback"

        # return self.sm
        return sm


if __name__ == "__main__":

    # path to wav_source that contains the audio of interest
    # wav_dir_path = (
    #     "/Users/peej/dev/uniden scanner "
    #     "scripts/uniden-api/kivy_gui/2019-07-17_15-04-13.wav"
    # )

    Config.set("kivy", "log_level", "info")

    # def get_child_names(ids):
    #     for index, child in enumerate(ids):
    #         print(f"[{index}] - {child}")

    # run the GUI
    DataWindowApp().run()
