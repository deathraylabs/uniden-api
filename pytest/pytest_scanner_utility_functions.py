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

    assert s.update_scanner_state()
    s.close()


def test_send_command():
    s = UnidenScanner()

    assert s.send_command("MDL")["MODEL_NAME"] == "SDS100"
    assert s.send_command("VER")["VERSION"] == "Version 1.10.00"
    s.close()


def test_get_response():
    s = UnidenScanner()

    s.serial.write(b"MDL\r")
    response = s.get_response()

    assert response["cmd"] == "MDL"
    assert response["data"] == ["SDS100"]
    # assert s.send_command("VER")["VERSION"] == "Version 1.10.00"

    # ridiculous writes should result in exception.
    s.serial.write(b"POO\r")

    try:
        s.get_response()
    except CommandError as e:
        assert type(CommandError()) == type(e)

    s.close()


def test_get_response_many_items():
    s = UnidenScanner()

    # get department quick key status for FL 0, Sys 0
    s.serial.write(b"DQK,0,0\r")
    response = s.get_response()
    data = response["data"]

    assert type(data) == type(list())
    assert len(data) == 100
    assert False

    s.close()


# if __name__ == "__main__":
#     test_get_wav_meta()
