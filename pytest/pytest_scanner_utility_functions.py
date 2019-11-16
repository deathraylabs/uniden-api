import pytest

from pathlib import Path
from scanner.scanner_utility_functions import *
from scanner.uniden import *


def test_get_wav_meta():
    # static test file
    directory = (
        "./scanner_test_data/BCDx36HP/audio/user_rec//4F067981/2019"
        "-08-06_15-12-35.wav"
    )
    p = Path(directory)

    meta_output = get_wav_meta(directory)
    assert meta_output["Site:Name"] == "98 HOU PubSafety NW Simulcast"
    assert meta_output["TGID:Name"] == "01 HPD-N"

    assert p.is_file()
    assert type(meta_output) == dict

    return meta_output


def test_files_with_matched_tags():
    """Check against test wav_source."""

    tag = "Red"
    directory = "./scanner_test_data/wav_files_for_testing"
    p = Path(directory)

    assert p.is_dir()

    files = files_with_matched_tags(directory, tag)

    assert type(files) == list

    test_list = [
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-07-17_15-04-13.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-07-23_10-56-56.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-07-26_07-23-34.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-07-29_10-37-55.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-07-31_09-31-12.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_09-04-27.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_09-18-21.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_09-46-31.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_09-53-25.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_09-53-29.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_09-53-38.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_10-25-57.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-01_10-38-09.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-02_18-06-36.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-02_18-07-17.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-02_18-40-26.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-02_18-46-25.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-02_18-48-51.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-02_18-57-22.wav",
        "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/2019-08-02_19-41-02.wav",
    ]

    assert len(files) == len(test_list)

    # assert str(files[2]) == test_list[2]


def test_get_directories():
    """Ensure get_directories utility function works."""

    d = (
        "/Users/peej/dev/uniden scanner "
        "scripts/uniden-api/pytest/scanner_test_data/BCDx36HP/audio/user_rec/4F067981/"
    )
    d_fake = "not a path"

    # catch incorrectly formatted paths
    assert get_directories(d_fake) is None
    assert type(get_directories(d)) == list
    assert len(get_directories(d)) == 3


# @pytest.fixture()
# def mass_storage():
#     """Mass storage test object"""
#     sd = UnidenMassStorage()
#     return sd


def test_mass_storage_initialized():
    sd = UnidenMassStorage()

    # root path is correct
    assert sd.d_root == Path("/Volumes/SDS100")


def test_get_audio_directories():
    sd = UnidenMassStorage(
        directory="/Users/peej/dev/uniden scanner "
        "scripts/uniden-api/pytest/scanner_test_data/"
    )

    sd.get_audio_directories()
    dirs = sd.audio_directories

    assert type(dirs) == list


def test_get_wav_files():
    sd = UnidenMassStorage()
    d = "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/BCDx36HP/audio/user_rec/4F067981/"
    d = Path(d)
    dirs = sd.get_wav_files(d)

    assert type(dirs) == list
    assert len(dirs) == 43


def test_open_scanner_port():
    s = UnidenScanner()
    assert s.open()
    s.close()


def test_update_scanner_state():
    s = UnidenScanner()

    assert s.update_scanner_state("pull")
    s.close()


def test_update_scanner_state_no_connection():
    """Update scanner state should return false if no connection."""
    s = UnidenScanner()
    s.close()

    assert s.update_scanner_state() is False


def test_send_command():
    s = UnidenScanner()

    assert s.send_command("MDL") == 4
    # nonsensical command
    assert s.send_command("POO,0,0") == 8
    # assert s.send_command("VER")["VERSION"] == "Version 1.10.00"
    s.close()


def test_get_response():
    """Check whether the get_response method is working correctly"""

    s = UnidenScanner()

    s.serial.write(b"MDL\r")
    response = s.get_response()

    assert response["cmd"] == "MDL"
    assert response["data"] == ["SDS100"]
    # assert s.send_command("VER")["VERSION"] == "Version 1.10.00"

    # ridiculous writes should result in exception.
    s.serial.write(b"POO\r")
    response = s.get_response()

    s.close()

    assert isinstance(response, str)


def test_get_response_many_items():
    s = UnidenScanner()

    # get department quick key status for FL 0, Sys 0
    s.serial.write(b"DQK,0,0\r")
    response = s.get_response()
    data = response["data"]

    assert type(data) == type(list())
    assert len(data) == 100

    s.close()


def test_read_and_decode_line():
    s = UnidenScanner()

    # get department quick key status for FL 0, Sys 0
    s.serial.write(b"MDL\r")
    response = s._read_and_decode_line()

    assert response == "MDL,SDS100\n"

    s.close()


def test_get_response_xml():
    """Test GSI response

    Notes:
        setup:
            - scanner must be set to home
    """

    s = UnidenScanner()

    # get department quick key status for FL 0, Sys 0
    s.serial.write(b"GSI\r")
    response = s.get_response()
    s.logger.debug(response)
    data = response["ScannerInfo"]["MonitorList"]["Name"]

    s.close()

    assert isinstance(response, dict)
    assert data == "Home"


def test_get_menu_view():
    s = UnidenScanner()
    view = s.get_menu_view()
    s.close()

    assert isinstance(type(view), type(dict))
    assert view["cmd"] == "MSI"


def test_open_menu():
    """check open menu functionality"""

    s = UnidenScanner()
    open_top_menu = s.open_menu(menu_id="TOP")

    # reset scanner view
    s.send_command("MSB,,RETURN_PREVIOUS_MODE")

    s.close()

    assert open_top_menu


def test_parse_time():
    """Function required to deal with time passed by scanner."""

    raw_timedate = "20010101000224"
    raw_timedate_end = "20010101000448"

    ptimedate = parse_time(raw_timedate, raw_timedate_end)

    assert ptimedate["TransmissionStart"]["date"] == "2001-01-01"
    assert ptimedate["TransmissionStart"]["time"] == "00:02:24"
    assert ptimedate["TransmissionEnd"]["date"] == "2001-01-01"
    assert ptimedate["TransmissionEnd"]["time"] == "00:04:48"
    assert ptimedate["PodcastDuration"] == "02:24"


def test_is_menu_screen():
    """Should show true or false depending on scanner state.

    Notes:
        - scanner must be connected to computer for this test.
    """
    s = UnidenScanner()
    s.update_scanner_state()

    menu_test = s.is_menu_screen()

    if s.scan_state["ScannerInfo"]["Mode"] == "Menu tree":
        assert menu_test is True

    s.close()


def test_get_volume():
    """Will pass test if scanner is setup according to proper configuration.

    Notes:
        Scanner Configuration:
        - volume: 1

    """
    s = UnidenScanner()
    s.update_scanner_state()

    vol = s.get_volume()

    s.close()

    assert vol == "1"


def test_get_list():
    """Test get_list method."""

    s = UnidenScanner()

    # this is an incorrect command, should be "favorites list"
    qk_list = s.get_list("favorites")

    assert qk_list is None

    qk_list = s.get_list("favorites list")
    assert isinstance(qk_list, dict)

    # test whether we get the correct list abbreviation
    assert qk_list["requested list abbrev"] == "FL"

    # test case with missing argument, should be "system", "0" for instance
    qk_list = s.get_list("system")
    assert qk_list is None

    # test case with correct argument structure
    qk_list = s.get_list("system", "8")
    assert isinstance(qk_list, dict)

    # test whether we get the correct list abbreviation
    assert qk_list["requested list abbrev"] == "SYS"

    s.close()

    assert True


def test_human_readable_qk_status():
    """Test human readable quick key status code"""

    s = UnidenScanner()

    fl_qk = s.get_fav_list_qk_status()
    qk_list = s.get_list("favorites list")

    assert s.get_human_readable_qk_status(fl_qk, qk_list)


def test_get_unit_id_name():
    """See if we can establish a connection to database"""

    # create instance of class to test
    db = UnidenLocalDatabase(
        db_path="/Users/peej/dev/uniden scanner scripts/uniden-api/databases/uniden.sqlite"
    )

    # unit ID for testing case with unit id name
    unit_id_name = db.get_unit_id_name("01")

    assert unit_id_name == "test_01"


# if __name__ == "__main__":
#     test_get_wav_meta()
