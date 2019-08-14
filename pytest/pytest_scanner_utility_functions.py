import pytest

from pathlib import Path
from scanner.scanner_utility_functions import *


def test_get_wav_meta():
    # static test file
    directory = "./scanner_test_data/4F067981/2019-08-06_15-12-35.wav"
    p = Path(directory)

    meta_output = get_wav_meta(directory)
    assert meta_output["Site:Name"] == "98 HOU PubSafety NW Simulcast"
    assert meta_output["Channel:Name"] == "01 HPD-N"

    assert p.is_file()
    assert type(meta_output) == dict

    return meta_output


def test_files_with_matched_tags():
    """Check against test directory."""

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

    d = "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/4F067981/"
    d_fake = "not a path"

    # catch incorrectly formatted paths
    assert get_directories(d_fake) is None
    assert type(get_directories(d)) == list
    assert len(get_directories(d)) == 3


# if __name__ == "__main__":
#     test_get_wav_meta()
